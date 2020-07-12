# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""Setup script for spyder_notebook."""

# Standard library imports
import ast
import distutils
import os
import os.path as osp
import pipes
import subprocess
import sys

# Third party imports
from setuptools import find_packages, setup
from setuptools.command.sdist import sdist

if sys.platform == 'win32':
    from subprocess import list2cmdline
else:
    def list2cmdline(cmd_list):
        """Convert list of arguments to a command line string."""
        return ' '.join(map(pipes.quote, cmd_list))


HERE = os.path.abspath(os.path.dirname(__file__))
SERVER_DIR = osp.join(HERE, 'spyder_notebook', 'server')
BUILD_DIR = osp.join(SERVER_DIR, 'build')


def run(cmd, *args, **kwargs):
    """Echo a command before running it."""
    distutils.log.info('> ' + list2cmdline(cmd))
    kwargs['shell'] = (sys.platform == 'win32')
    return subprocess.check_call(cmd, *args, **kwargs)


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


class my_sdist(sdist):
    """Extension for the default sdist command."""

    def run(self):
        """Copmpile JavaScript and then do the default run()."""
        if not osp.isdir(BUILD_DIR):
            run(['jlpm', 'install'], cwd=SERVER_DIR)
            run(['jlpm', 'build'], cwd=SERVER_DIR)
        sdist.run(self)


# Verify that BUILD_DIR exist before trying to build wheels
if any([arg == 'bdist_wheel' for arg in sys.argv]):
    if not osp.isdir(BUILD_DIR):
        print("\nERROR: Server components are missing!! Please run "
              "'python setup.py sdist' first.\n")
        sys.exit(1)


REQUIREMENTS = ['spyder>=4.1,<5', 'jinja2', 'jupyter_core', 'nbformat',
                'notebook>=4.3', 'qtpy', 'qdarkstyle', 'requests', 'traitlets']

setup(
    name='spyder-notebook',
    version=get_version(),
    cmdclass={'sdist': my_sdist},
    keywords='spyder jupyter notebook',
    python_requires='>=3.5',
    url='https://github.com/spyder-ide/spyder-notebook',
    license='MIT',
    author='Spyder Development Team',
    description='Jupyter notebook integration with Spyder',
    long_description="This package allows the Jupyter notebook "
                     "to run inside Spyder as a plugin.",
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    include_package_data=True,
    classifiers=['Development Status :: 4 - Beta',
                 'Framework :: Jupyter',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3']
)
