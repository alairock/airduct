from souffle.scheduling import Schedule, task


schedule = Schedule(
    name='ExampleFlow3',
    run_at='* * * * *',
    flow=[
        task('read_users'),
        task('e3f2'),
        task('e3f3', can_fail=True),
        task('e3f4')
    ]
)


async def read_users():
    print('yo read users')
    # for i in range(10000):  # need to process a LOT of tasks
    #     await send_to_worker(process_a_worker_task(i))


async def process_a_worker_task(payload):
    pass


async def e3f2():
    print('e3f2')


async def e3f3():
    print('e3f3')


async def e3f4():
    print('e3f4')
