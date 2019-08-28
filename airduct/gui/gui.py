from flask import Flask, escape, request, render_template
import os
import webbrowser
from airduct.database import setup_config

def create_app():
    app = Flask(__name__)
    def run_on_start(*args, **argv):
        url = "http://127.0.0.1:5000"
        webbrowser.open(url,new=2)
        print('Opening Browser...')
    run_on_start()
    return app
app = create_app()


def run(config):
    os.environ['AIRDUCT_CONFIG_FILE'] = config or ''
    setup_config()
    app.run()

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return render_template('home.html', name=name)
