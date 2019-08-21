import pickle
import datetime
import uuid
import os
from souffle.logger import logger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, and_

Base = declarative_base()
DB_TYPE = os.getenv('DATABASE_TYPE')
Session = sessionmaker()

engine = None
if DB_TYPE == 'postgres':
    pass
    # TODO: handle postgres connection
elif DB_TYPE == 'mysql':
    pass
    # TODO: handle mysql connection

elif  DB_TYPE == 'sqlite':
    DATABASE_FILE = 'example.db'
    engine = create_engine(f'sqlite:///{DATABASE_FILE}', echo=False)
else:
    engine = create_engine('sqlite:///:memory:', echo=False)

Session.configure(bind=engine)


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
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Flow(Base):
    __tablename__ = 'flows'

    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer)
    status = Column(String)
    name = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    run_at = Column(String)
    flow = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


def initdb():
    logger.info('Setting up database tables')
    Base.metadata.create_all(engine)
    logger.info('Complete setting up database tables')


def fetch_schedules():
    session = Session()
    results = session.query(Schedule).all()
    return results


def has_concurrent_flow(schedule):
    session = Session()
    r = session.query(Flow).filter(Flow.name.in_([schedule.name])).filter(Flow.status.in_(['InProgress'])).all()
    if len(r) > 0:
        return True
    return False


def create_flow_record(schedule):
    session = Session()
    flow = Flow(name=schedule.name, schedule_id=schedule.id, status='InProgress')
    session.add(flow)
    session.commit()
    return flow


def create_task_record(flow_id, parents, step, task, pickled_task):
    session = Session()
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
    session = Session()
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
    session = Session()
    session.query(Task).filter(Task.id == task.id).update({
        'status': status,
        'completed_at': datetime.datetime.now(),
        'logs': message
    })
    session.commit()
    if status is 'Error' and not can_fail:
        return
    _update_children(task)


def _update_children(task):
    session = Session()
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
    session = Session()
    session.query(Flow).filter(Flow.id == flow_id).update({
        'status': status
    })
    session.commit()
