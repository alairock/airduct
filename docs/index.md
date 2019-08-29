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

## Environment Variables
Environment variables allow you to override your configuration file settings, helping keep secrets out of your repo.

### Axing Ambiguity
Some of these environment variables migt be generic enough to collide with your own env vars or your dependencies vars. To overcome this, set a prefix, which will allow you to namespace your airduct env vars.

- `ENV_PREFIX`

For example `ENV_PREFIX=AIRDUCT_` will force airduct to look for it's environment variables with `AIRDUCT_` at the beginning. eg. `AIRDUCT_DB_NAME`

### Database env vars
Airduct uses Sqlalchemy, so you can use any database in Airduct that Sqlalchemy can. Airduct has exposed much of the Sqlalchemy configuration, see below.

- `DB_VERBOSE` - Default `False`. Noisy verboseness from sqlalchemy's logger
- `DB_ENCODING` - Default `utf-8`. See Sqlalchemy for options
- `DB_DIALECT` - Default `sqlite`. The database type you want to use.
- `DB_DRIVER` - The database driver the dialect uses.
- `DB_USER` - Database username. Not required.
- `DB_PASS` - Database password. Not required
- `DB_HOSTNAME` - Default `localhost`
- `DB_PORT` - Required for most dialects
- `DB_NAME` - Required, no defaults
- `DB_SQLITE_FILE` - Required if you wish to use non-in-memory sqlite
- `DB_DSN` - If you just want to pass your own DSN

## Config File
The config file allows you to define your database connection without setting environment variables.

example file:

```yaml
db:
#  sqlite:
#    file: example.db
  dialect: mysql
  driver: pymysql
  user: guest
  pass: guest
  port: 3306
  host: localhost
  name: mydb
  verbose: false

```

## GUI
The gui is a simple react app. There is no security currently added to the web app, so you may want to limit where you deploy the webapp, or just run it locally. 

To run:

```bash
$ cd webapp
$ yarn install
$ yarn start
```
