# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# -----------------------------------------------------------------------------

"""Spyder Notebook plugin."""

# Local imports
from spyder_notebook.notebookplugin import NotebookPlugin as PLUGIN_CLASS

VERSION_INFO = (0, 1, 0, 'dev0')
__version__ = '.'.join(map(str, VERSION_INFO))

PLUGIN_CLASS
