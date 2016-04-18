#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from distutils.core import setup

setup(
    name='python-taskpaper',
    version='0.3',

    author='Alex Chan',
    author_email='alex@alexwlchan.net',

    packages = ["taskpaper"],
    description = "A module for interacting with TaskPaper-styled documents",
    url = 'https://github.com/alexwlchan/python-taskpaper',

    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ]
)