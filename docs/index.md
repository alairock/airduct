# airduct
Simple Pipeline Scheduler in Python

## Links

- [Github](https://github.com/alairock/airduct)
- [Documentation](https://airduct.readthedocs.io)

## Installing
    $ pip install airduct

or

    $ poetry add airduct

## Quickstart
Airduct calls pipelines "flows". A flow is a python file with a very particular definition, which is hopefully self explanatory.

Here is an example flow:

```python
from airduct import schedule, task


schedule(
    name='ExampleFlow',
    run_at='* * * * *',
    flow=[
        task('e1f1'),
        [task('e1f2'), task('e1f3', can_fail=True)],
        [task('e1f4')]
    ]
)

async def e1f1():
    print('e1f1 - An async function!')

def e1f2():
    print('e1f2 - Regular functions work too')

async def e1f3():
    print('e1f3')

async def e1f4():
    print('e1f4')
```

A flow requires a `airduct.scheduling.schedule` which runs at scheduler initialization. 
The schedule function requires:
 - `name`: A name to identify the flow as, must be unique
 - `run_at`: A crontab-like scheduling syntax. (Uses this [crontab parser](https://github.com/josiahcarlson/parse-crontab))
 - `flow`: A list of `airduct.scheduling.task`'s. These can be nested lists, for parallel tasks, 2 levels deep. See example.

`task()` Requires the name of the function you desire to run during that step. Must be defined in the same flow file. You can ignore errors with `can_fail=True` in the function's signature.

This file is placed in a folder/python-module alongside other flows.

To run: `$ airduct schedule --path /path/to/flow/folder`

By default it uses a sqlite in-memory database. If using the in-memory database, it will also automatically run as a worker, in addition to a scheduler.

## Commands

### scheduler
Start the scheduler, schedules flows.
Options:
- `-p` or `--path` path to your flows directory
- `-c` or `--config` path to your config.yaml
- `-w` or `--run-with-worker` wun scheduler and worker in one process
- `--help` shows available options

### worker
Run this command to work on scheduled flows' tasks.
Options:
- `-c` or `--config` path to your config.yaml
- `--help` shows available options


### trigger
Trigger a flow, outside of it's defined schedule
Options:
- `-c` or `--config` path to your config.yaml
- `--help` shows available options
