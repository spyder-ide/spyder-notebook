# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""Spyder notebook default configuration."""

CONF_SECTION = 'notebook'

CONF_DEFAULTS = [
    (
        CONF_SECTION,
        {
            'recent_notebooks': [],    # Items in "Open recent" menu
            'opened_notebooks': [],    # Notebooks to open at start
            'theme': 'same as spyder'  # Notebook theme (light/dark)
        }
    )
]

# IMPORTANT NOTES:
# 1. If you want to *change* the default value of a current option, you need to
#    do a MINOR update in config version, e.g. from 1.0.0 to 1.1.0
# 2. If you want to *remove* options that are no longer needed in our codebase,
#    or if you want to *rename* options, then you need to do a MAJOR update in
#    version, e.g. from 1.0.0 to 2.0.0
# 3. You don't need to touch this value if you're just adding a new option
CONF_VERSION = '0.1.0'
