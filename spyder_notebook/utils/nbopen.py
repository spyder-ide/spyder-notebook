# -*- coding: utf-8 -*
#
# Copyright (c) 2014, Thomas Kluyver and contributors to the nbopen
# project: https://github.com/takluyver/nbopen
# All rights reserved.
#
# Licensed under the terms of BSD 3-clause license

"""Open notebooks using the best available server."""

import atexit
import os.path
import subprocess
import time

from notebook import notebookapp
from spyder.config.base import get_home_dir


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
    filename = os.path.abspath(filename)
    home_dir = get_home_dir()
    server_info = find_best_server(filename)

    if server_info is not None:
        print("Using existing server at", server_info['notebook_dir'])
        return server_info
    else:
        if filename.startswith(home_dir):
            nbdir = home_dir
        else:
            nbdir = os.path.dirname(filename)

        print("Starting new server")
        command = ['jupyter', 'notebook', '--no-browser',
                   '--notebook-dir={}'.format(nbdir),
                   '--NotebookApp.password=']
        if os.name == 'nt':
            creation_flag = 0x08000000 # CREATE_NO_WINDOW
        else:
            creation_flag = 0 # Default value
        proc = subprocess.Popen(command, creationflags=creation_flag)
        atexit.register(proc.terminate)

        # Wait ~10 secs for the server to be up
        for _x in range(40):
            server_info = find_best_server(filename)
            if server_info is not None:
                break
            else:
                time.sleep(0.25)

        if server_info is None:
            raise NBServerError()

        return server_info
