from souffle import schedule, task


schedule(
    name='ExampleFlow',
    run_at='* * * * *',
    flow=[
        task('read_users'),
        [task('e1f2'), task('e1f3', can_fail=True)],
        [task('e1f4')]
    ]
)


async def read_users():
    print('yo read users')
    # for i in range(10000):  # need to process a LOT of tasks
    #     await send_to_worker(process_a_worker_task(i))


async def process_a_worker_task(payload):
    pass


async def e1f2():
    print('e1f2')
    raise Exception("Testing a complete failure")


async def e1f3():
    print('e1f3')
    raise Exception("Testing a complete failure")


async def e1f4():
    print('e1f4')

