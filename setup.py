# -*- coding: utf-8 -*-
#
# This file is part of Flask-Wiki
# Copyright (C) 2020 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms

"""
Flask-Wiki
-------------

This is the description for that library
"""
from setuptools import setup, find_packages

install_requires = [
    'Bootstrap-Flask',
    'Flask',
    'Flask-Babel',
    'Flask-WTF',
    'Markdown',
    'WTForms',
]

setup(
    name='Flask-Wiki',
    version='0.0.1',
    url='http://github.com/jma/flask-wiki/',
    license='BSD',
    author='Johnny Mariéthoz',
    author_email='Johnny.Mariethoz@rero.ch',
    description='A simple file based wiki using Flask.',
    long_description=__doc__,
    py_modules=['flask_wiki'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=install_requires
)
