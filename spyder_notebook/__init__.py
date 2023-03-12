# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# -----------------------------------------------------------------------------

"""Spyder Notebook plugin."""

# Local imports
from spyder_notebook.notebookplugin import NotebookPlugin as PLUGIN_CLASS
from spyder_notebook._version import __version__


# Connect to Jupyter
def _jupyter_server_extension_paths():
    return [{'module': 'spyder_notebook'}]


def _jupyter_server_extension_points():
    from spyder_notebook.server.main import SpyderNotebookApp

    return [{'module': 'spyder_notebook', 'app': SpyderNotebookApp}]


def _jupyter_labextension_paths():
    return [{'src': 'labextension', 'dest': '@spyder-notebook/lab-extension'}]

PLUGIN_CLASS
