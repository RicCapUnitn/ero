#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='eroproject',
      version='0.0.1',
      description='Ero: events relevance optimization',
      packages=['eroproject', 'tools'],
      package_dir={'': 'src',
                   'tools': './'}
      )
