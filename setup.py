#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='sphinx-multiversion',
    description='Add support for multiple versions to sphinx',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        "Programming Language :: Python :: 3",
      ],
    author='Jan Holthuis',
    author_email='holthuis.jan@googlemail.com',
    version="1.0.0",
    install_requires=['sphinx >= 2.1'],
    license='BSD',
    packages=['sphinx_multiversion'],
    entry_points={
        'console_scripts': [
            'sphinx-multiversion=sphinx_multiversion:main',
        ],
    },
 )
