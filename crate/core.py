#!/usr/bin/env python
import sys
import json
import uuid
import logging
import asyncio
import traceback
from typing import Any
from typing import Dict
from typing import Tuple

__all__ = ['Server', 'Client', 'Crate']


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)-5s][%(asctime)s][crate] %(message)s',
    stream=sys.stderr)


class Server(asyncio.Protocol):
    def __init__(self, app, loop):
        self.app = app
        self.loop = loop

        self.log = logging.getLogger('server')

        super().__init__()

    def _jsonify(self, **kwargs):
        return json.dumps(kwargs).encode('utf-8')

    def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        self.log.debug(
            'Connection accepted from {}:{}'.format(*self.address))

    def data_received(self, data):
        message = json.loads(data.decode())
        task_name = message.get('task')
        task_args = message.get('args', [])
        task_kwargs = message.get('kwargs', {})

        # If data received contains a task name
        if task_name:
            # Retrieve task method in registrar
            task_func = self.app._registrar.get(task_name)

            # If no method has been retrieved, this is an unregistered task
            if not task_func:
                self.log.info(
                    'Unregistered "{}" task received'.format(task_name))
                self.transport.write(self._jsonify(
                    success=False, message='Unregistered task.'))
                return

            task_uuid = str(uuid.uuid4())
            self.log.info('(task:{}) Running task...'.format(task_uuid))

            try:
                # Send task coroutine to loop
                self.loop.create_task(task_func(*task_args, **task_kwargs))
                self.log.info('(task:{}) Task sent.'.format(task_uuid))
                # Send to client task uuid
                self.transport.write(
                    self._jsonify(success=True, message=task_uuid))
            except Exception as err:
                self.log.info(
                    '(task:{}) Error while running task...\n{}'.format(
                        task_uuid, traceback.format_exc()))
                # Send to client task uuid and traceback
                self.transport.write(
                    self._jsonify(
                        success=False, error=str(err),
                        message=task_uuid, traceback=traceback.format_exc()))
        else:
            self.log.info('Invalid message received: {}'.format(data))


class Client(asyncio.Protocol):
    def __init__(self, message: Dict, loop: asyncio.AbstractEventLoop):
        super().__init__()
        self.message = message
        self.loop = loop
        self.result = {}

        self.log = logging.getLogger('client')

    def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        self.log.debug('Connecting to {}:{}'.format(*self.address))

        data = json.dumps(self.message)
        transport.write(data.encode('utf-8'))

        self.log.debug('Sending {!r}'.format(data))
        if transport.can_write_eof():
            transport.write_eof()

    def data_received(self, data):
        self.log.debug('Received {!r}'.format(data))
        self.result = json.loads(data.decode('utf-8'))

    def connection_lost(self, exc):
        self.log.debug('Server closed connection')
        self.transport.close()
        self.loop.stop()
        super().connection_lost(exc)


class Crate:
    def __init__(self, host: str = 'localhost', port: int = 6666):
        self.host = host
        self.port = port
        self.log = logging.getLogger('crate')

        self._registrar = {}
        self._loop = asyncio.get_event_loop()

    def __del__(self):
        if self._loop:
            self._loop.close()

    def run(self):
        self.log.info('Listening on {}:{}...'.format(self.host, self.port))

        factory = self._loop.create_server(
            lambda: Server(self, self._loop), self.host, self.port)
        server = self._loop.run_until_complete(factory)
        try:
            self._loop.run_forever()
        finally:
            self.log.info('Closing server')
            server.close()
            self._loop.run_until_complete(server.wait_closed())
            self.log.debug('Closing event loop')
            self._loop.close()

    def task(self, *args: Any, **kwargs: Any):
        def delay(app, name, *args, **kwargs):
            return app.send_task(name, args, kwargs)

        method = args[0]
        method.delay = lambda *args, **kwargs: delay(
            self, method.__name__, *args, **kwargs)
        self._registrar[method.__name__] = method

        return method

    def send_task(
            self, name: str, args: Tuple = tuple(), kwargs: Dict = {}) -> Dict:

        coroutine = self._loop.create_connection(lambda: Client(
            {'task': name, 'args': args, 'kwargs': kwargs}, self._loop),
            self.host, self.port)

        transport, client = self._loop.run_until_complete(coroutine)
        self._loop.run_forever()

        return client.result
