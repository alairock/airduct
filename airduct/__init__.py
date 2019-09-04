from airduct.database import Schedule, Task, Flow, get_session
import inspect
import pickle


class TaskNotFoundError(AttributeError):
    pass


class FlowNestingTooDeep(Exception):
    pass


def schedule(name, run_at, flow):
    session = get_session()
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    _schedule = Schedule(name=name, run_at=run_at, flow=pickle.dumps(flow), originated_file=module.__name__)
    for _task in flow:
        if type(_task) is list:
            for t in _task:
                if type(t) is list:
                    raise FlowNestingTooDeep('Reached max nesting level in flow. Only 2 levels allowed')
    r = session.query(Schedule).filter(Schedule.name == name).first()
    if r is not None:
        # There is already a schedule, let's update it
        r.run_at = run_at
        r.flow = pickle.dumps(flow)
        session.commit()
        return
    session.add(_schedule)
    session.commit()


def task(name, can_fail=False):
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    return pickle.dumps({'module': mod.__name__, 'func_name': name, 'can_fail': can_fail})
