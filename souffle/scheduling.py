import uuid
from souffle.tasks import Task


class Schedule:
    def __init__(self, name, run_at, flow):
        self.name = name
        self.schedule = run_at
        self.flow = flow
        self.id = str(uuid.uuid4())

    def _add_id_to_tasks(self):
        for _task in self.flow:
            if type(_task) is list:
                for _t in _task:
                    _t.schedule_id = self.id
            else:
                _task.schedule_id = self.id


def task(name, can_fail=False):
    _task = Task(name, can_fail=can_fail)
    return _task
