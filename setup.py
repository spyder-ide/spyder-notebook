# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder_notebook/__init__.py for details)


"""
Spyder notebook plugin
======================

Jupyter notebook integration with Spyder.
"""

# Standard library imports
import ast
import os

# Third party imports
from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))


def get_version(module='spyder_notebook'):
    """Get version."""
    with open(os.path.join(HERE, module, '_version.py'), 'r') as f:
        data = f.read()
    lines = data.split('\n')
    for line in lines:
        if line.startswith('VERSION_INFO'):
            version_tuple = ast.literal_eval(line.split('=')[-1].strip())
            version = '.'.join(map(str, version_tuple))
            break
    return version


REQUIREMENTS = ['spyder>=4', 'notebook>=4.3',
                'qtpy', 'requests', 'psutil', 'nbformat']

setup(
    name='spyder-notebook',
    version=get_version(),
    keywords='spyder jupyter notebook',
    url='https://github.com/spyder-ide/spyder-notebook',
    license='MIT',
    author='Spyder Development Team',
    description='Jupyter notebook integration with Spyder',
    long_description="This package allows the Jupyter notebook "
                     "to run inside Spyder as a plugin.",
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=REQUIREMENTS,
    include_package_data=True,
    classifiers=['Development Status :: 4 - Beta',
                 'Framework :: Jupyter',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3']
)
