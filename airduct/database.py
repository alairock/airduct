import pickle
import datetime
from airduct.logger import logger
from airduct.config import getenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, and_, PickleType
from sqlalchemy.sql import func


Base = declarative_base()
ENGINE = None
Session = sessionmaker()
SeshCache = None


def setup_config():
    global ENGINE, Session
    verbose = getenv('DB_VERBOSE', False)
    encoding = getenv('DB_ENCODING', 'utf-8')
    dialect = '+'.join([x for x in [getenv('DB_DIALECT', 'sqlite'), getenv('DB_DRIVER', None)] if x is not None])
    credentials = ':'.join([getenv('DB_USER', ''), getenv('DB_PASS', '')]) + '@'
    hostname = getenv('DB_HOSTNAME')
    dbport = ':' + str(getenv('DB_PORT')) if getenv('DB_PORT') is not None else ''
    dbname = '/' + getenv('DB_NAME') if getenv('DB_NAME') is not None else ''
    sqlite_file = getenv('DB_SQLITE_FILE', ':memory:')
    colon_style = f':///{sqlite_file}' if getenv('DB_DIALECT', 'sqlite') == 'sqlite' else '://'
    dsn = getenv('DB_DSN', f'{dialect}{colon_style}{credentials}{hostname}{dbport}{dbname}')
    if getenv('DB_DIALECT', 'sqlite') == 'sqlite':
        dsn = 'sqlite' + colon_style
    Session = sessionmaker()
    ENGINE = create_engine(dsn, encoding=encoding, echo=verbose)
    Session.configure(bind=ENGINE)


def get_session():
    global SeshCache
    if SeshCache is None:
        SeshCache = Session()
        return SeshCache
    return SeshCache

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    status = Column(String)
    flow_id = Column(Integer)
    parents = Column(PickleType)
    step = Column(Integer)
    pickled_task = Column(PickleType)
    can_fail = Column(Boolean)
    logs = Column(String)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Flow(Base):
    __tablename__ = 'flows'

    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer)
    status = Column(String)
    name = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    run_at = Column(String)
    flow = Column(PickleType)
    originated_file = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


def initdb():
    setup_config()
    logger.info('Setting up database tables')
    Base.metadata.create_all(ENGINE)
    logger.info('Complete setting up database tables')
    return get_session()


def fetch_schedules():
    session = get_session()
    results = session.query(Schedule).all()
    return results


def fetch_schedule(name):
    session = get_session()
    results = session.query(Schedule).filter(Schedule.name == name).first()
    return results

def fetch_flows():
    session = get_session()
    current_time = datetime.datetime.utcnow()
    yesterday = current_time - datetime.timedelta(days=7)
    return session.query(Flow) \
        .filter(Flow.created_at >= yesterday) \
        .order_by(Flow.created_at.desc()) \
        .limit(10) \
        .all()

def fetch_flow(name):
    session = get_session()
    return session.query(Flow).filter(Flow.name.in_([name]))\
        .order_by(Flow.created_at.desc()).all()

def fetch_tasks(flow_id):
    session = get_session()
    return session.query(Task).filter(Task.flow_id == flow_id)\
        .order_by(Task.step.asc()).all()

def has_concurrent_flow(schedule):
    session = get_session()
    r = session.query(Flow).filter(Flow.name.in_([schedule.name])).filter(Flow.status.in_(['InProgress'])).all()
    if len(r) > 0:
        return True
    return False


def create_flow_record(schedule):
    session = get_session()
    flow = Flow(name=schedule.name, schedule_id=schedule.id, status='InProgress')
    session.add(flow)
    session.commit()
    return flow


def create_task_record(flow_id, parents, step, task, pickled_task):
    session = get_session()
    task = Task(
        flow_id=flow_id,
        parents=None if len(parents) == 0 else pickle.dumps(parents),
        step=step,
        can_fail=task.get('can_fail', False),
        pickled_task=pickled_task
    )
    session.add(task)
    session.commit()
    return task


def fetch_task():
    session = get_session()
    # TODO: Check if flow is older than timeout period. If it is, then don't include in these results
    results = session.query(Flow, Task) \
        .join(Task, and_(Task.flow_id == Flow.id, Task.status.is_(None)), isouter=True) \
        .filter(Flow.status == 'InProgress') \
        .filter(Task.parents.is_(None)) \
        .order_by(Task.step) \
        .first()

    if results is None:
        return results
    task = results[1]
    if task is None:
        return task
    task.status = 'InProgress'
    session.commit()
    return task


def mark_task(task, status="Complete", can_fail=False, message=''):
    session = get_session()
    session.query(Task).filter(Task.id == task.id).update({
        'status': status,
        'completed_at': datetime.datetime.now(),
        'logs': message
    })
    session.commit()
    if status is 'Error' and not can_fail:
        mark_flow(task.flow_id, status=status)
        return
    if status is not 'Complete':
        mark_flow(task.flow_id, status=status)
        return
    _update_children(task)


def _update_children(task):
    session = get_session()
    results = session.query(Task).filter(Task.flow_id == task.flow_id).filter(Task.step == int(task.step)+1).all()
    for r in results:
        if not isinstance(r.parents, str):
            parents = None if r.parents is None else pickle.loads(r.parents)
            new_parents = None if parents is None else parents.remove(task.id)
            r.parents = None if new_parents is None or len(new_parents) == 0 else pickle.dumps(new_parents)
    session.commit()
    if len(results) == 0:
        logger.info(f'Flow ended: {task.flow_id}')
        mark_flow(task.flow_id)
        return


def mark_flow(flow_id, status='Complete'):
    session = get_session()
    session.query(Flow).filter(Flow.id == flow_id).update({
        'status': status
    })
    session.commit()
