import click
import asyncio
from souffle.core import start_scheduler, start_worker
loop = asyncio.get_event_loop()


@click.group()
def cli():
    pass


@click.option('--path', prompt=True)
@click.command(help="Start a worker")
def worker(path):
    click.echo('Starting a Worker')
    start_worker(path)


@click.command(help="Start the scheduler")
@click.option('--path', prompt=True)
def scheduler(path):
    click.echo('Starting Scheduler...')
    start_scheduler(path)


@click.command(help="Trigger a schedule by name")
def trigger():
    click.echo('Run a schedule by name')


cli.add_command(worker)
cli.add_command(scheduler)
cli.add_command(trigger)

if __name__ == '__main__':
    cli()

