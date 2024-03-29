import subprocess
import click
import asyncio
from airduct.core import start_scheduler, start_worker, trigger_schedule
from airduct.api.api import run as api_run
import signal
loop = asyncio.get_event_loop()


@click.group()
def cli():
    pass


def receive_signal(signal_number, frame):
    print('Received:', signal_number)
    raise SystemExit('Exiting')


signal.signal(signal.SIGTERM, receive_signal)


@click.command(help="Start a worker")
@click.option('--config', help='Path to your config.yml')
def worker(config):
    click.echo('Starting a Worker')
    start_worker(config)


@click.command(help="Start the scheduler")
@click.option('-p', '--path', '_path', prompt=True)
@click.option('-c', '--config', '_config', help='Path to your config.yml')
@click.option('-w', '--run_with_worker', '_no_worker', default=False)
def scheduler(_path, _config, _no_worker):
    click.echo('Starting Scheduler...')
    click.echo(f'Loding config from: {_config}')
    start_scheduler(_path, _config, _no_worker)


@click.command(help="Trigger a schedule by name")
@click.option('-c', '--config', '_config', help='Path to your config.yml')
@click.argument('name')
def trigger(_config, name):
    trigger_schedule(_config, name)
    click.echo('Run a schedule by name')


@click.command(help="Start the webapp's api server")
@click.option('-c', '--config', '_config', help='Path to your config.yml')
def api(_config):
    api_run(_config)


@click.command(help="Build a version of the webapp for production")
@click.option('--host', help="BaseURL for API. default: http://localhost:5000", default="http://localhost:5000")
@click.option('--web-host', help='Default is relative paths, change this if you need morec control over paths')
@click.option('--require-login', help='Require login for api requests, (using basic auth)', is_flag=True)
def webapp(host, web_host, require_login):
    print('host:', host, 'show_login:', require_login)
    from pathlib import Path
    import tempfile
    click.echo('You must have node/yarn and wget installed on your system.')

    with tempfile.TemporaryDirectory() as dirpath:
        subprocess.call(
            ['wget', 'https://github.com/alairock/airduct-gui/archive/master.zip'],
            cwd=dirpath,
        )
        subprocess.call(
            ['unzip', 'master.zip'],
            cwd=dirpath,
        )
        cwd = str(Path(dirpath) / 'airduct-gui-master')

        subprocess.call(
            ['yarn', 'install'],
            cwd=cwd,
        )
        subprocess.call(
            ['yarn', 'build'],
            cwd=cwd,
            env={'REACT_APP_API_URL': host or '',
                 'PUBLIC_URL': web_host or '',
                 'REACT_APP_REQUIRE_LOGIN': str(require_login).lower()}
        )
        subprocess.call(
            ['mv', cwd+'/build', 'build']
        )

        click.echo('To serve now, you can use: $ cd build && python3 -m http.server')


cli.add_command(worker)
cli.add_command(scheduler)
cli.add_command(trigger)
cli.add_command(api)
cli.add_command(webapp)

if __name__ == '__main__':
    cli()

