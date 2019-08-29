from flask import Flask, escape, request, jsonify
from flask_cors import CORS
import os
import webbrowser
from airduct.database import setup_config, fetch_schedules, fetch_flows, fetch_tasks

def create_app():
    app = Flask(__name__)
    def run_on_start(*args, **argv):
        url = "http://127.0.0.1:5000"
        webbrowser.open(url,new=2)
        print('Opening Browser...')
    # run_on_start()
    return app
app = create_app()
CORS(app, resources={r"/*": {"origins": "*"}})

def run(config):
    os.environ['AIRDUCT_CONFIG_FILE'] = config or ''
    setup_config()
    app.run()

@app.route('/api/schedules')
def schedules():
    schedules = fetch_schedules()
    def transform(schedule):
        return {
            'id': schedule.id,
            'run_at': schedule.run_at,
            'name': schedule.name,
            'originated_file': schedule.originated_file,
            'created_at': None if schedule.created_at is None else schedule.created_at.strftime("%b %d %Y %H:%M:%S"),
            'updated_at': None if schedule.updated_at is None else schedule.updated_at.strftime("%b %d %Y %H:%M:%S")
        }
    return jsonify([transform(x) for x in schedules])

@app.route('/api/flows/<string:names>')
def flows(names):
    print(names)
    flows = fetch_flows(names)
    def transform(flow):
        return {
            'id': flow.id,
            'schedule_id': flow.schedule_id,
            'name': flow.name,
            'status': flow.status,
            'created_at': None if flow.created_at is None else flow.created_at.strftime("%b %d %Y %H:%M:%S"),
            'updated_at': None if flow.updated_at is None else flow.updated_at.strftime("%b %d %Y %H:%M:%S")
        }
    return jsonify([transform(x) for x in flows])


@app.route('/api/tasks/<string:flow_id>')
def tasks(flow_id):
    tasks = fetch_tasks(flow_id)
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
    return jsonify([transform(x) for x in tasks])
