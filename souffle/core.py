import asyncio
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
import inspect
from souffle.logger import logger


warnings.simplefilter(action='ignore', category=FutureWarning)


def _start_task(flow, parents, step, task, pickled_task):
    task = create_task_record()
    return task


def start_flow(schedule):
    if has_concurrent_flow(schedule):
        logger.info('Job in progress, skipping to prevent duplicate work.')
        return
        # TODO: Maybe allow multiple flows to run, but this needs to be a configuration

    flow = create_flow_record(schedule)
    step = 0
    parents = []
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


def start_scheduler(path, no_worker=True):
    initdb()
    find_flow_files(path)
    schedules = fetch_schedules()
    while True:
        for schedule in schedules:
            if crontab.CronTab(schedule.run_at).test(datetime.datetime.now()):
                start_flow(schedule)
        if no_worker:
            work_on_tasks()
        time.sleep(1)


def work_on_tasks():
    task = fetch_task()
    if task is None:
        return
    # TODO: Handle/fetch timed out tasks

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
    # TODO: Handle long running processes/multiple process handling.
    mark_task(task)
    logger.info(f'Task finished: {task.id}')


def start_worker():
    while True:
        work_on_tasks()
