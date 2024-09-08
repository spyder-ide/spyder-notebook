# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for plugin config dialog."""

from unittest.mock import MagicMock

# Test library imports
import pytest
from qtpy.QtWidgets import QMainWindow

# Local imports
from spyder.api.plugin_registration._confpage import PluginsConfigPage
from spyder.api.plugin_registration.registry import PLUGIN_REGISTRY
from spyder_notebook.notebookplugin import NotebookPlugin


class MainWindowMock(QMainWindow):
    register_shortcut = MagicMock()
    editor = MagicMock()

    def __getattr__(self, attr):
        return MagicMock()


@pytest.mark.parametrize(
    'config_dialog',
    # [[MainWindowMock, [ConfigPlugins], [Plugins]]]
    [[MainWindowMock, [], [NotebookPlugin]]],
    indirect=True)
def test_config_dialog(config_dialog):
    # Check that Notebook config page works
    configpage = config_dialog.get_page()
    assert configpage
    configpage.save_to_conf()

    # Check that Plugins config page works with notebook plugin
    # Regression test for spyder-ide/spyder-notebook#470
    PLUGIN_REGISTRY.set_all_internal_plugins(
        {NotebookPlugin.NAME: (NotebookPlugin.NAME, NotebookPlugin)}
    )
    plugins_config_page = PluginsConfigPage(PLUGIN_REGISTRY, config_dialog)
    plugins_config_page.initialize()
