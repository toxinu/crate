Crate
=====

Crate is a lightweight Python (3.5) coroutine worker (*à la Celery*) to allow asynchronous tasks into your application.

Getting started
---------------

Create your `my_crate.py` into your project:

.. code-block:: python

    import asyncio
    from datetime import datetime

    from crate import Crate

    app = Crate()


    @app.task
    async def hello_world(waiting: int=2) -> None:
        print('[{}] Hello world!'.format(datetime.now()))
        await asyncio.sleep(waiting)
        print('[{}] Wumba lumba dub dub...'.format(datetime.now()))

And run your worker:

.. code-block:: bash

    crate --app my_crate:app


You can call tasks in two different ways:

.. code-block:: python

    # If you have access to task code

    from my_crate import hello_world

    hello_world.delay()

    # Or just task name

    from crate import Crate

    app = Crate()
    app.send_task('hello_world')
..

More
----

Some examples in *example.py*.

Want to do file system I/O? aiofiles_

Want to do http requests? aiohttp_

Want to do postgresql? aiopg_

License is MIT.


.. _aiofiles: https://github.com/Tinche/aiofiles
.. _aiohttp: https://aiohttp.readthedocs.io/en/stable/
.. _aiopg: https://aiopg.readthedocs.io/en/stable/
