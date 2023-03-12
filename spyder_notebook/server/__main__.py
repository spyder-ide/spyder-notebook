# Copyright (c) Jupyter Development Team, Spyder Project Contributors.
# Distributed under the terms of the Modified BSD License.

"""CLI entry point for Spyder Notebook server."""

import sys

from spyder_notebook.server.main import main

sys.exit(main())
