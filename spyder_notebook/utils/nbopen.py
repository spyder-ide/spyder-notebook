# -*- coding: utf-8 -*
#
# Copyright (c) 2014, Thomas Kluyver and contributors to the nbopen
# project: https://github.com/takluyver/nbopen
# All rights reserved.
#
# Licensed under the terms of BSD 3-clause license

import atexit
import os.path
import subprocess
import time

from notebook import notebookapp
from notebook.utils import url_path_join, url_escape
from spyder.config.base import get_home_dir


class NBServerError(Exception):
    """Exception for notebook server errors."""


def find_best_server(filename):
    """Find the best server to open a notebook with."""
    servers = [si for si in notebookapp.list_running_servers() \
               if filename.startswith(si['notebook_dir'])]
    try:
        return max(servers, key=lambda si: len(si['notebook_dir']))
    except ValueError:
        return None


def get_url(filename, server_inf):
    """Get url given by a notebook server to filename."""
    path = os.path.relpath(filename, start=server_inf['notebook_dir'])
    url = url_path_join(server_inf['url'], 'notebooks', url_escape(path))
    return url


def nbopen(filename):
    """Open a notebook using the best available server."""
    filename = os.path.abspath(filename)
    home_dir = get_home_dir()
    server_inf = find_best_server(filename)

    if server_inf is not None:
        print("Using existing server at", server_inf['notebook_dir'])
        url = get_url(filename, server_inf)
        return url
    else:
        if filename.startswith(home_dir):
            nbdir = home_dir
        else:
            nbdir = os.path.dirname(filename)

        print("Starting new server")
        command = 'jupyter notebook --no-browser'
        proc = subprocess.Popen(command.split(), cwd=nbdir)
        atexit.register(proc.terminate)

        # Wait ~7.5 secs for the server to be up
        for _x in range(30):
            server_inf = find_best_server(filename)
            if server_inf is not None:
                break
            else:
                time.sleep(0.25)

        if server_inf is None:
            raise NBServerError()

        url = get_url(filename, server_inf)
        return url
