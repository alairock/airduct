from airduct import schedule, task


schedule(
    name='ExampleFlow2',
    run_at='* * * * *',
    flow=[
        task('read_users'),
        [task('e2f2'), task('e2f3', can_fail=True)],
        task('e2f4')
    ]
)


def read_users():
    print('yo read users')
    # for i in range(10000):  # need to process a LOT of tasks
    #     await send_to_worker(process_a_worker_task(i))


async def process_a_worker_task(payload):
    pass


async def e2f2():
    print('e2f2')


async def e2f3():
    print('e2f3')


async def e2f4():
    print('e2f4')
