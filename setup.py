from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='django_redis_logger',
    version='1.0',
    packages=['django_redis_logger'],
    long_description=open(join(dirname(__file__), 'README.md')).read(),
)
