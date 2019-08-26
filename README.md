# airduct
Simple Pipeline Scheduler in Python

## Documentation

[airduct.readthedocs.io](https://airduct.readthedocs.io)

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

A flow requires a `airduct.scheduling.Schedule` object assigned to a `schedule` variable. The Schedule object requires:
 - `name`: A name to identify the flow as
 - `run_at`: A crontab-like scheduling syntax. (Uses this [crontab parser](https://github.com/josiahcarlson/parse-crontab))
 - `flow`: A list of `airduct.scheduling.task`'s. These can be nested lists, but only 2 levels deep. 
 
`task()` Requires the name of the function you desire to run during that step. Must be defined in that flow file.

This file is placed in a folder/python-module alongside other flows. 

Then to run, there are two commands. 
 - `airduct schedule --path /path/to/flow/folder`
 - `airduct work --path /path/to/flow/folder`
