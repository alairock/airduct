from souffle.database import Schedule, Task, Flow, Session
import inspect
import pickle


class TaskNotFoundError(AttributeError):
    pass


class FlowNestingTooDeep(Exception):
    pass


def schedule(name, run_at, flow):
    session = Session()
    _schedule = Schedule(name=name, run_at=run_at, flow=pickle.dumps(flow))
    for _task in flow:
        if type(_task) is list:
            for t in _task:
                if type(t) is list:
                    raise FlowNestingTooDeep('Reached max nesting level in flow. Only 2 levels allowed')
    session.add(_schedule)
    session.commit()


def task(name, can_fail=False):
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    return pickle.dumps({'module': mod.__name__, 'func_name': name, 'can_fail': can_fail})
