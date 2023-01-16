import asyncio
import sighandler

q = asyncio.Queue()


async def producer():
    print(f'Producer {q=}')

    n = 0
    while True:
        await asyncio.sleep(1)
        await q.put(n)
        print(f'Producer: {n=}')
        n = n + 1


async def consumer():
    print(f'Consumer {q=}')

    while True:
        n = await q.get()
        print(f'Consumer: {n=}')
        q.task_done()


async def main():
    sighandler.register();

    async with asyncio.TaskGroup() as tg:
        tg.create_task(producer())
        tg.create_task(consumer())

    print('End')


if __name__ == '__main__':
    asyncio.run(main())
