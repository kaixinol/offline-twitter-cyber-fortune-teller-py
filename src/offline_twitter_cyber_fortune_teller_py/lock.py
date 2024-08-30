import asyncio

lock: dict[int, bool] = {}
mutex = asyncio.Lock()


async def update(data: dict):
    global lock
    async with mutex:
        lock |= data
        print(lock)


async def get():
    global lock
    async with mutex:
        return lock
