import asyncio
import os
import pickle
import crontab
import importlib
from souffle import logger
from souffle.flowfinder import find_flow_files
from souffle.database import mark_task, has_concurrent_flow, create_flow_record, \
    create_task_record, fetch_task, initdb, fetch_schedules
import warnings
import time
import datetime
from souffle.logger import logger


warnings.simplefilter(action='ignore', category=FutureWarning)


def start_flow(schedule):
    if has_concurrent_flow(schedule):
        logger.info('Job in progress, skipping to prevent duplicate work.')
        return
        # TODO: Maybe allow multiple flows to run, but this needs to be a configuration

    flow = create_flow_record(schedule)
    step = 0
    parents = []
    logger.info(f'Starting flow: {flow.id}, schedule {flow.schedule_id}')
    for task in pickle.loads(schedule.flow):
        if type(task) is list:
            future_parents = []
            for t in task:
                _task = create_task_record(flow.id, parents, step, pickle.loads(t), t)
                future_parents.append(_task.id)
        else:
            _task = create_task_record(flow.id, parents, step, pickle.loads(task), task)
            future_parents = [_task.id]
        parents = future_parents
        step += 1


def start_scheduler(path, config, no_worker=False):
    os.environ['SOUFFLE_CONFIG_FILE'] = config
    session = initdb()
    find_flow_files(path)
    schedules = fetch_schedules()
    while True:
        for schedule in schedules:
            if crontab.CronTab(schedule.run_at).test(datetime.datetime.now()):
                start_flow(schedule)
        if no_worker or str(session.bind.url) == 'sqlite:///:memory:':
            work_on_tasks()
        time.sleep(1)


def start_worker(config):
    os.environ['SOUFFLE_CONFIG_FILE'] = config
    initdb()
    while True:
        if work_on_tasks() == 'sleep':
            time.sleep(1)  # No work to do, let's not cruise so fast, and pound the db.
            # Maybe make this configurable in the futer


def work_on_tasks():
    task = fetch_task()
    if task is None:
        return 'sleep'

    logger.info(f'Starting task: {task.id}')
    task_definition = pickle.loads(task.pickled_task)
    module = importlib.import_module(task_definition['module'])
    try:
        task_func = getattr(module, task_definition['func_name'])
    except AttributeError:
        msg = f'{task.function_name} not found in {module.__file__}'
        logger.error(msg)
        raise Exception(msg)
    except Exception as e:
        logger.error(f'An unknown error happened: {e}')
        raise e

    try:
        # TODO: If task is taking too long, then kill it. This would be a configurable field on the Task object.
        # eg: `if start_time + task.timout > now(): Kill task_func
        if asyncio.iscoroutinefunction(task_func):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(task_func())
        else:
            task_func()
    except Exception as e:
        if not task.can_fail:
            logger.error(f'Something bad happened. {e}')
            mark_task(task, 'Error', message=str(e))
            return
        logger.debug(f'An error happened but your task configuration allowed it. {e}')
        mark_task(task, 'Error', message=str(e))
        return
    mark_task(task)
    logger.info(f'Task finished: {task.id}')
