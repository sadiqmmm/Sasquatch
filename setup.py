#!/usr/bin/env python

import sys

from setuptools import setup, find_packages

from simple import version

long_description = """
long description.
"""

setup(
    name='Simple',
    version=version,
    description='Simple',
    long_description=long_description,
    author='Todd Cullen',
    author_email='todd@thoughtleadr.com',
    url='http://www.github.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'simple = simple:main',
        ]
    },
    classifiers=[
          'Development Status :: 5 - Production/Stable',
    ],
)