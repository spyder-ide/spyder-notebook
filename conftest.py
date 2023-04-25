# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Configuration file for Pytest."""

# Standard library imports
import os

# To activate/deactivate certain things in Spyder when running tests.
# NOTE: Please leave this before any other import here!!
os.environ['SPYDER_PYTEST'] = 'True'

# Third-party imports
import pytest


@pytest.fixture(autouse=True)
def reset_conf_before_test():
    from spyder.config.manager import CONF
    CONF.reset_to_defaults(notification=False)
