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

# Third party imports
from setuptools import find_packages, setup
from spyder_notebook import __version__

REQUIREMENTS = ['spyder>=3.1.4', 'notebook>=4.3']

setup(
    name='spyder-notebook',
    version=__version__,
    keywords='spyder jupyter notebook',
    url='https://github.com/spyder-ide/spyder-notebook',
    license='MIT',
    author='Spyder Development Team',
    description='Jupyter notebook integration with Spyder',
    long_description="This package allows the Jupyter notebook "
                     "to run inside Spyder as a plugin.",
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=REQUIREMENTS,
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python 2.7',
                 'Programming Language :: Python 3']
)
