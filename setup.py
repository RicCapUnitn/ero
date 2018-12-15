#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='eroproject',
      version='0.0.1',
      description='Ero: events relevance optimization',
      packages=['eroproject'],
      package_dir={'': 'src'}
      )

setup(name='tools',
      version='0.0.1',
      description='Ero: events relevance optimization',
      packages=['tools']
      )
