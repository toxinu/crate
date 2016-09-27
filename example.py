import asyncio
from datetime import datetime

try:
    import aiofiles
except ImportError:
    print('Must install aiofiles')
    exit(1)

try:
    import aiohttp
    import async_timeout
except ImportError:
    print('Must install aiohttp')
    exit(1)


from crate import Crate

app = Crate()


@app.task
async def write_log(line: str) -> None:
    async with aiofiles.open('./crate.log', 'a+') as f:
        await f.write("[{}] {}\n".format(datetime.now(), line))

    await asyncio.sleep(5)

    async with aiofiles.open('./crate.log', 'a+') as f:
        await f.write("[{}] {}\n".format(datetime.now(), line[::-1]))


@app.task
async def hello_world(waiting: int=2) -> None:
    print('[{}] Hello world!'.format(datetime.now()))
    await asyncio.sleep(waiting)
    print('[{}] Wumba lumba dub dub...'.format(datetime.now()))


@app.task
async def fib(n: int) -> int:
    if n <= 1:
        print('fib({}) -> {}'.format(n, n))
        return n
    else:
        a = await fib(n - 1)
        b = await fib(n - 2)
        print('fib({}) -> {}'.format(n, a + b))
        return a + b


@app.task
async def fetch_url(url: str, with_text: bool=False) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print('[{}] {} {}'.format(datetime.now(), resp.status, url))
            if with_text:
                print(await resp.text())

if __name__ == "__main__":
    app.run()
