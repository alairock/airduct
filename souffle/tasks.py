import uuid
from souffle.database import mark_task


class Task:
    def __init__(self, func_name, can_fail=False):
        self.id = str(uuid.uuid4())
        self.flow_id = None
        self.step = None
        self.schedule_id = None
        self.module_path = None
        self.function_name = func_name
        self.can_fail = can_fail
        self.complete = False
        self.started = False

    def mark_complete(self, status="Complete"):
        mark_task(self, status=status)
        self.complete = True

    def mark_failure(self, e):
        self.complete = True
        mark_task(self, status="Error", update_children=False)
