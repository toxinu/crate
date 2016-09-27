#!/usr/bin/env python
# coding: utf-8
import os
import re
import sys

from codecs import open

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


version = ''
with open('crate/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='crate',
    version=version,
    description='l',
    author="Geoffrey Lehée",
    author_email="contact@toxi.nu",
    url='https://github.com/toxinu/crate/',
    keywords="",
    packages=['crate'],
    package_dir={'crate': 'crate'},
    entry_points={
        'console_scripts': [
            'crate = crate.__main__:main']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5']
)
