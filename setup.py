#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='MPKLoader',
    version='0.1',
    description='Daemon for loading data from MPK website',
    author='mic4ael',
    author_email='crossner90@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
        'beautifulsoup4',
        'sqlalchemy',
        'psycopg2',
        'lxml'
    ],
    entry_points={
        'console_scripts': [
            'loader = loader.main:run'
        ]
    }
)
