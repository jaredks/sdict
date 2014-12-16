#!/usr/bin/env python

from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

with open('CHANGES.rst') as f:
    changes = f.read()

setup(
    name='sdict',
    version='0.1.0',
    description='dict subclass with slicing and insertion.',
    author='Jared Suttles',
    url='https://github.com/jaredks/sdict',
    py_modules=['sdict'],
    package_data={'': ['LICENSE', 'README.rst', 'CHANGES.rst']},
    long_description=readme + '\n\n' + changes,
    license='BSD License'
)
