import pickle
import datetime
from souffle.logger import logger
from souffle.config import getenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, and_
from sqlalchemy.sql import func


Base = declarative_base()
ENGINE = None
Session = sessionmaker()


def _setup_config():
    global ENGINE, Session
    verbose = getenv('DB_VERBOSE', False)
    encoding = getenv('DB_ENCODING', 'utf-8')
    dialect = '+'.join([getenv('DB_DIALECT', 'sqlite'), getenv('DB_DRIVER', '')])
    credentials = ':'.join([getenv('DB_USER', ''), getenv('DB_PASS', '')]) + '@'
    hostname = getenv('DB_HOSTNAME')
    dbport = ':' + getenv('DB_PORT') if getenv('DB_PORT') is not None else ''
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
    return Session()


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    status = Column(String)
    flow_id = Column(Integer)
    parents = Column(String)
    step = Column(Integer)
    pickled_task = Column(String)
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
    flow = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


def initdb():
    _setup_config()
    logger.info('Setting up database tables')
    Base.metadata.create_all(ENGINE)
    logger.info('Complete setting up database tables')
    return get_session()


def fetch_schedules():
    session = get_session()
    results = session.query(Schedule).all()
    return results


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
        parents=str(parents) if len(parents) == 0 else pickle.dumps(parents),
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
        .filter(Task.parents.is_('[]')) \
        .first()

    if results is None:
        return results
    task = results[1]
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
        mark_flow(task.flow_id)
        return
    _update_children(task)


def _update_children(task):
    session = get_session()
    results = session.query(Task).filter(Task.flow_id == task.flow_id).filter(Task.step == int(task.step)+1).all()
    for r in results:
        if not isinstance(r.parents, str):
            parents = pickle.loads(r.parents)
            new_parents = parents.remove(task.id)
            r.parents = str([]) if not new_parents or len(new_parents) == 0 else pickle.dumps(new_parents)
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
