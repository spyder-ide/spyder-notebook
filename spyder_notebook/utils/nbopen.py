# -*- coding: utf-8 -*
#
# Copyright (c) 2014, Thomas Kluyver and contributors to the nbopen
# project: https://github.com/takluyver/nbopen
# All rights reserved.
#
# Licensed under the terms of BSD 3-clause license

"""Open notebooks using the best available server."""

import atexit
import logging
import os
import os.path as osp
import subprocess
import sys
import time

from notebook import notebookapp

from spyder.config.base import DEV, get_home_dir, get_module_path


# Kernel specification to use in notebook server
KERNELSPEC = 'spyder.plugins.ipythonconsole.utils.kernelspec.SpyderKernelSpec'

logger = logging.getLogger(__name__)


class NBServerError(Exception):
    """Exception for notebook server errors."""


def find_best_server(filename):
    """Find the best server to open a notebook with."""
    servers = [si for si in notebookapp.list_running_servers()
               if filename.startswith(si['notebook_dir'])]
    try:
        return max(servers, key=lambda si: len(si['notebook_dir']))
    except ValueError:
        return None


def nbopen(filename):
    """
    Open a notebook using the best available server.

    Returns information about the selected server.
    """
    filename = osp.abspath(filename)
    home_dir = get_home_dir()
    server_info = find_best_server(filename)

    if server_info is not None:
        logger.debug('Using existing server at %s',
                     server_info['notebook_dir'])
        return server_info
    else:
        if filename.startswith(home_dir):
            nbdir = home_dir
        else:
            nbdir = osp.dirname(filename)

        logger.debug("Starting new server")
        serverscript = osp.join(osp.dirname(__file__), '../server/main.py')
        command = [sys.executable, serverscript, '--no-browser',
                   '--notebook-dir={}'.format(nbdir),
                   '--NotebookApp.password=',
                   "--KernelSpecManager.kernel_spec_class='{}'".format(
                           KERNELSPEC)]

        if os.name == 'nt':
            creation_flag = 0x08000000  # CREATE_NO_WINDOW
        else:
            creation_flag = 0  # Default value

        if DEV:
            env = os.environ.copy()
            env["PYTHONPATH"] = osp.dirname(get_module_path('spyder'))
            subprocess.Popen(command, creationflags=creation_flag, env=env)
        else:
            subprocess.Popen(command, creationflags=creation_flag)

        # Wait ~25 secs for the server to be up
        for _x in range(100):
            server_info = find_best_server(filename)
            if server_info is not None:
                break
            else:
                time.sleep(0.25)

        if server_info is None:
            raise NBServerError()

        # Kill the server at exit
        atexit.register(notebookapp.shutdown_server, server_info, log=logger)

        return server_info
