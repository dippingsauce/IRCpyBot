#-*- coding: utf-8 -*-

"""
    githubris
    ~~~~~~~~~

    Setup
    `````

    $ pip install -e .
"""

from distutils.core import setup
import os

setup(
    name='githubris',
    version='0.0.1',
    url='',
    author='dippingsauce, mek',
    author_email='dippingsaucespm@gmail.com',
    packages=[
        'configs',
        ],
    platforms='any',
    license='Pending',
    install_requires=[
    ],
    scripts=[
        "scripts/pyrc"
        ],
    description="basic irc bot written in python",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
)
