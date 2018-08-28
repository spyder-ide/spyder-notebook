# -*- coding: utf-8 -*
#
# Copyright (c) 2014, Thomas Kluyver and contributors to the nbopen
# project: https://github.com/takluyver/nbopen
# All rights reserved.
#
# Licensed under the terms of BSD 3-clause license

"""Open notebooks using the best available server."""

import atexit
import os
import os.path as osp
import subprocess
import sys
import time

from notebook import notebookapp
import psutil

from spyder.config.base import DEV, get_home_dir, get_module_path


try:
    # Spyder 4
    from spyder.plugins.ipythonconsole.utils.kernelspec import SpyderKernelSpec
    KERNELSPEC = ('spyder.plugins.ipythonconsole.utils'
                  '.kernelspec.SpyderKernelSpec')
except ImportError:
    # Spyder 3
    KERNELSPEC = 'spyder.utils.ipython.kernelspec.SpyderKernelSpec'


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
        print("Using existing server at", server_info['notebook_dir'])
        return server_info
    else:
        if filename.startswith(home_dir):
            nbdir = home_dir
        else:
            nbdir = osp.dirname(filename)

        print("Starting new server")
        command = [sys.executable, '-m', 'notebook', '--no-browser',
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
            proc = subprocess.Popen(command, creationflags=creation_flag,
                                    env=env)
        else:
            proc = subprocess.Popen(command, creationflags=creation_flag)

        # Kill the server at exit. We need to use psutil for this because
        # Popen.terminate doesn't work when creationflags or shell=True
        # are used.
        def kill_server_and_childs(pid):
            ps_proc = psutil.Process(pid)
            for child in ps_proc.children(recursive=True):
                child.kill()
            ps_proc.kill()

        atexit.register(kill_server_and_childs, proc.pid)

        # Wait ~25 secs for the server to be up
        for _x in range(100):
            server_info = find_best_server(filename)
            if server_info is not None:
                break
            else:
                time.sleep(0.25)

        if server_info is None:
            raise NBServerError()

        return server_info
