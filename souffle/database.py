import sqlite3
import pickle
import datetime
import uuid
from souffle.logger import logger

DATABASE_FILE = 'example.db'


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(e)
    return None


def start_flow(flow):
    task_id = str(uuid.uuid4())
    conn = create_connection(DATABASE_FILE)
    with conn:
        sql = '''
            SELECT status FROM flows WHERE flows.name = :name ORDER BY created_at DESC
        '''
        cur = conn.cursor()
        cur.execute(sql, {'name': flow.name})
        record = cur.fetchone()
        last_status = False if record is None else record[0]
        if last_status == 'InProgress':
            logger.info('Job in progress, skipping to prevent duplicate work.')
            return
        # TODO: Maybe allow multiple flows to run, but this needs to be a configuration
    with conn:
        logger.info(f'Starting job: {flow.id}')
        sql = '''
            INSERT INTO flows(id, created_at, updated_at, name, status)
                VALUES(:id, :now, :now, :name, :status)
        '''
        cur = conn.cursor()
        cur.execute(sql, {'id': task_id,
                          'now': str(datetime.datetime.now()),
                          'name': flow.name,
                          'status': 'InProgress'})
        return task_id


def init_task(flow_id, parents, step, task):
    _id = str(uuid.uuid4())
    conn = create_connection(DATABASE_FILE)

    sql = '''
        INSERT INTO tasks(id, created_at, updated_at, flow_id, can_fail, parents, step, pickled_task) 
                VALUES(:id, :now, :now, :flow_id, :can_fail, :parents, :step, :func)
    '''
    with conn:
        conn.cursor()
        conn.execute(sql, {'now': str(datetime.datetime.now()),
                           'id': _id,
                           'flow_id': flow_id,
                           'can_fail': task.can_fail,
                           'parents': str(parents) if len(parents) == 0 else pickle.dumps(parents),
                           'step': step,
                           'func': pickle.dumps(task)})
    return _id


def _fetch_task(conn):
    sql = '''
        SELECT tasks.*
        FROM flows
        LEFT JOIN tasks ON tasks.flow_id = flows.id AND tasks.status IS NULL
        WHERE flows.status = 'InProgress'
        AND tasks.parents = '[]'
    '''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchone()


def _update_task_status(conn, _id, status='InProgress'):
    sql = '''
        UPDATE tasks SET status = :status WHERE id = :id
    '''
    cur = conn.cursor()
    cur.execute(sql, {'id': _id, 'status': status})


def fetch_task():
    conn = create_connection(DATABASE_FILE)
    with conn:
        record = _fetch_task(conn)
        if not record:
            return
        _update_task_status(conn, record['id'])
    task = pickle.loads(record['pickled_task'])
    task.id = record['id']
    return task


def _update_child(conn, record, new_parents):
    sql = '''
        UPDATE tasks SET parents = :parents WHERE id = :id
    '''
    cur = conn.cursor()
    cur.execute(sql, {
        'id': record['id'],
        'parents': str([]) if not new_parents or len(new_parents) == 0 else pickle.dumps(new_parents),

    })


def _mark_flow(conn, flow_id, status="Complete"):
    sql = '''
        UPDATE flows SET status = :status WHERE id = :id
    '''
    cur = conn.cursor()
    cur.execute(sql, {
        'status': status,
        'id': flow_id
    })


def _update_children(conn, task):
    sql = '''
        SELECT * FROM tasks WHERE flow_id = :flow_id AND step = :step
    '''
    cur = conn.cursor()
    cur.execute(sql, {'flow_id': task.flow_id, 'step': int(task.step) + 1})
    record = None
    for record in cur.fetchall():
        new_parents = None
        if not isinstance(record['parents'], str):
            parents = pickle.loads(record['parents'])
            new_parents = parents.remove(task.id)
        _update_child(conn, record, new_parents)
    if not record:
        logger.info(f'Flow ended: {task.flow_id}')
        _mark_flow(conn, task.flow_id)
        return


def mark_task(task, status='Complete', update_children=True):
    conn = create_connection(DATABASE_FILE)
    with conn:
        _update_task_status(conn, task.id, status=status)
        if update_children:
            _update_children(conn, task)
        else:
            _mark_flow(conn, task.flow_id)


def sync_schedules(flows):
    initdb()
    conn = create_connection(DATABASE_FILE)
    with conn:
        cur = conn.cursor()

        sql = '''
            INSERT INTO schedules(created_at, updated_at, name, schedule) 
                VALUES(:now, :now, :name, :schedule)
            ON CONFLICT(name) 
                DO UPDATE SET updated_at=:now, schedule=:schedule
        '''
        for flow in flows:
            cur.execute(sql, {'name': flow.name,
                              'schedule': flow.schedule,
                              'now': str(datetime.datetime.now())})
    return flows


def initdb():
    logger.info('Setting up database tables')
    conn = create_connection(DATABASE_FILE)
    with conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS schedules
                     (created_at text, 
                     updated_at text, 
                     name text PRIMARY KEY, 
                     schedule text)
        ''')
        cur.execute('''CREATE TABLE IF NOT EXISTS flows
                 (created_at text, 
                 updated_at text, 
                 id text PRIMARY KEY,
                 name text,
                 status text)
        ''')
        cur.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (created_at text, 
                 updated_at text, 
                 completed_at text,
                 status text,
                 logs text,
                 id text PRIMARY KEY, 
                 flow_id text,
                 can_fail boolean,
                 parents text,
                 step integer, 
                 pickled_task text)
        ''')
    logger.info('Complete setting up database tables')
