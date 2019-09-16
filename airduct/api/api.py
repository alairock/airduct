from functools import wraps

from flask import Flask, jsonify
from flask_cors import CORS
import os

from airduct.config import getenv
from airduct.database import setup_config, fetch_schedules, fetch_flows, fetch_flow, fetch_tasks
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
auth = HTTPBasicAuth()
CORS(app, resources={r"/*": {"origins": "*"}})


@auth.verify_password
def verify_password(username, password):
    username = getenv('BASIC-AUTH_USERNAME')
    password = getenv('BASIC-AUTH_PASSWORD')
    if username is None or password is None:
        raise Exception('Cannot have blank username or password.')
    users = {
        username: generate_password_hash(password)
    }
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


def run_wsgi(config):
    os.environ['AIRDUCT_CONFIG_FILE'] = config or ''
    setup_config()
    return app


def run(config):
    os.environ['AIRDUCT_CONFIG_FILE'] = config or ''
    setup_config()
    return app.run(port=getenv('AIRDUCT_PORT', 8339))


old_login_required = auth.login_required


def optional_require(func):
    @wraps(func)
    def inside_optional_require():
        require_login = getenv('BASIC-AUTH_ENABLED', False)
        if require_login:
            # mad props to @matt from pythondev.slack.com for () at the end of old_login_required(func)()
            return old_login_required(func)()
        else:
            return func()
    return inside_optional_require


auth.login_required = optional_require


@app.route('/heartbeat')
def heartbeat():
    return jsonify({'success': True})


@app.route('/')
def home():
    return jsonify({'success': True})


@app.route('/api/schedules')
@auth.login_required
def schedules():
    _schedules = fetch_schedules()

    def transform(schedule):
        return {
            'id': schedule.id,
            'run_at': schedule.run_at,
            'name': schedule.name,
            'originated_file': schedule.originated_file,
            'created_at': None if schedule.created_at is None else schedule.created_at.strftime("%b %d %Y %H:%M:%S"),
            'updated_at': None if schedule.updated_at is None else schedule.updated_at.strftime("%b %d %Y %H:%M:%S")
        }
    return jsonify([transform(x) for x in _schedules])


@app.route('/api/flows')
@auth.login_required
def flows():
    _flows = fetch_flows()

    def transform(flow):
        return {
            'id': flow.id,
            'schedule_id': flow.schedule_id,
            'name': flow.name,
            'status': flow.status,
            'created_at': None if flow.created_at is None else flow.created_at.strftime("%b %d %Y %H:%M:%S"),
            'updated_at': None if flow.updated_at is None else flow.updated_at.strftime("%b %d %Y %H:%M:%S")
        }
    return jsonify([transform(x) for x in _flows])


@app.route('/api/flows/<string:names>')
@auth.login_required
def get_flows(names):
    _flows = fetch_flow(names)

    def transform(flow):
        return {
            'id': flow.id,
            'schedule_id': flow.schedule_id,
            'name': flow.name,
            'status': flow.status,
            'created_at': None if flow.created_at is None else flow.created_at.strftime("%b %d %Y %H:%M:%S"),
            'updated_at': None if flow.updated_at is None else flow.updated_at.strftime("%b %d %Y %H:%M:%S")
        }
    return jsonify([transform(x) for x in _flows])


@app.route('/api/tasks/<string:flow_id>')
@auth.login_required
def tasks(flow_id):
    _tasks = fetch_tasks(flow_id)

    def transform(task):
        return {
            'id': task.id,
            'flow_id': task.flow_id,
            'step': task.step,
            'status': task.status,
            'can_fail': task.can_fail,
            'completed_at': None if task.completed_at is None else task.completed_at.strftime("%b %d %Y %H:%M:%S"),
            'created_at': None if task.created_at is None else task.created_at.strftime("%b %d %Y %H:%M:%S"),
            'updated_at': None if task.updated_at is None else task.updated_at.strftime("%b %d %Y %H:%M:%S")
        }
    return jsonify([transform(x) for x in _tasks])
