import asyncio
import os
import pickle
import crontab
import importlib
from airduct import logger
from airduct.flowfinder import find_flow_files
from airduct.database import mark_task, has_concurrent_flow, create_flow_record, \
    create_task_record, fetch_task, initdb, fetch_schedules, fetch_schedule, setup_config
import warnings
import time
import datetime
from airduct.logger import logger


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
    os.environ['AIRDUCT_CONFIG_FILE'] = config or ''
    session = initdb()
    flows = find_flow_files(path)
    schedules = fetch_schedules()
    # We use set.difference() here instead of ^ since we only want what is the database and not in the files
    removed_modules = set([x.originated_file for x in schedules]).difference(set(flows))
    while True:
        now = datetime.datetime.now()
        for schedule in schedules:
            if schedule.originated_file in removed_modules:
                continue
            if crontab.CronTab(schedule.run_at).test(now):
                start_flow(schedule)
        if no_worker or str(session.bind.url) == 'sqlite:///:memory:':
            work_on_tasks()
        # rare edge case: If there are so many jobs that it takes longer than
        # 1 minute to schedule all of them and it misses the next
        # minute and that next minute had new tasks to schedule, it will miss them.
        time.sleep(1)


def trigger_schedule(config, name):
    os.environ['AIRDUCT_CONFIG_FILE'] = config or ''
    setup_config()
    schedule = fetch_schedule(name)
    if schedule is not None:
        start_flow(schedule)


def start_worker(config):
    os.environ['AIRDUCT_CONFIG_FILE'] = config
    initdb()
    while True:
        if work_on_tasks() == 'sleep':
            time.sleep(1)  # No work to do, let's not cruise so fast, and pound the db.
            # Maybe make this configurable in the futer


def _load_module(task):
    module = None
    task_definition = {"module": ""}
    try:
        task_definition = pickle.loads(task.pickled_task)
        module = importlib.import_module(task_definition['module'])
        task_func = getattr(module, task_definition['func_name'])
        return task_func
    except AttributeError:
        msg = f'{task.function_name} not found in {module.__file__}'
        raise Exception(msg)
    except ModuleNotFoundError as e:
        raise Exception(f'Module not found, maybe it doesnt exist anymore? '
                        f'{task_definition["module"]}')


def work_on_tasks():
    task = fetch_task()
    if task is None:
        return 'sleep'

    logger.info(f'Starting task: {task.id}, Flow: {task.flow_id}')
    try:
        task_func = _load_module(task)
        # TODO: If task is taking too long, then kill it. This would be a configurable field on the Task object.
        # eg: `if start_time + task.timout > now(): Kill task_func
        if asyncio.iscoroutinefunction(task_func):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(task_func())
        else:
            task_func()
    except KeyboardInterrupt as e:
        print('KeyboardInterrupt: Marking task as such.')
        mark_task(task, 'Interrupted')
        raise e
    except SystemExit as e:
        print('System exiting: Marking task as such.')
        mark_task(task, 'SIGTERM', message='System asked to exit, handling exit.')
        raise SystemExit from e
    except Exception as e:
        if not task.can_fail:
            logger.error(f'Something bad happened. {e}')
            mark_task(task, 'Error', message=str(e))
            return
        logger.debug(f'An error happened but your task configuration allowed it. {e}')
        mark_task(task, 'Error', can_fail=True, message=str(e))
        return
    mark_task(task)
    logger.info(f'Task finished: {task.id}, Flow: {task.flow_id}')
