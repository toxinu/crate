import os
import sys
import argparse
from importlib import import_module


def main():
    parser = argparse.ArgumentParser(description='Crate worker.')
    parser.add_argument(
        '--app', '-A', default='app:app',
        help='crate application path (default: app:app)')
    parser.add_argument(
        '--host', '-H', default='localhost',
        help='default crate bind (default: localhost)')
    parser.add_argument(
        '--port', '-P', default=6666,
        help='default crate port (default: 6666)')
    args = parser.parse_args()

    sys.path.insert(0, os.path.dirname(__file__))
    module_name = args.app.split(':')[0]
    app_name = args.app.split(':')[-1]

    print('Loading {}:{}...'.format(module_name, app_name))
    module = import_module(module_name)
    app = getattr(module, app_name)

    app.host = args.host
    app.port = args.port

    print('Starting the crate on {}:{}...'.format(app.host, app.port))
    app.run()
