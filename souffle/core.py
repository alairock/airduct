import asyncio

import crontab
import importlib
from souffle import logger
from souffle.flowfinder import find_flows
from souffle.database import sync_schedules, start_flow, init_task, fetch_task
import warnings
import time
import datetime
import inspect


warnings.simplefilter(action='ignore', category=FutureWarning)


def start_scheduler(path):
    flows = find_flows(path)
    sync_schedules(flows)
    while True:
        for flow in flows:
            if crontab.CronTab(flow.schedule).test(datetime.datetime.now()):
                step = 0
                parents = []
                flow_id = start_flow(flow)
                if flow_id:
                    for task in flow.flow:
                        if type(task) is list:
                            future_parents = []
                            for t in task:
                                t.flow_id = flow_id
                                t.step = step
                                task_id = init_task(flow_id, parents, step, t)
                                future_parents.append(task_id)
                        else:
                            task.step = step
                            task.flow_id = flow_id
                            task_id = init_task(flow_id, parents, step, task)
                            future_parents = [task_id]
                        parents = future_parents
                        step += 1

        time.sleep(1)


def start_worker(path):
    while True:
        task = fetch_task()
        # TODO: Handle/fetch timed out tasks
        if not task:
            time.sleep(1)
            continue
        logger.logger.info(f'Starting task: {task.id}')
        module = importlib.import_module(task.module_path)
        try:
            task_func = getattr(module, task.function_name)
        except AttributeError as e:
            msg = f'{task.function_name} not found in {module.__file__}'
            logger.logger.error(msg)
            raise Exception(msg)
        try:
            if inspect.iscoroutinefunction(task_func):
                loop = asyncio.get_event_loop()
                loop.run_until_complete(task_func())
            else:
                task_func()
        except Exception as e:
            if not task.can_fail:
                logger.logger.error(f'Something bad happened. {e}')
                task.mark_failure(e)
                continue
            logger.logger.debug(f'An error happened but your configuration allowed it. {e}')
            task.mark_complete(status="Error")
            continue
        # TODO: Handle long running processes/multiple process handling.
        task.mark_complete()
        logger.logger.info(f'Task finished: {task.id}')
