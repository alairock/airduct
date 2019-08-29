import click
import asyncio
from airduct.core import start_scheduler, start_worker, trigger_schedule
from airduct.api.api import run as gui_run
loop = asyncio.get_event_loop()


@click.group()
def cli():
    pass


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


@click.command(help="Start a webserver for the GUI")
@click.option('-c', '--config', '_config', help='Path to your config.yml')
def gui(_config):
    gui_run(_config)


cli.add_command(worker)
cli.add_command(scheduler)
cli.add_command(trigger)
cli.add_command(gui)

if __name__ == '__main__':
    cli()

