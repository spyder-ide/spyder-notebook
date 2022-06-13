# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for config.py"""

# Third-party library imports
import pytest

# Spyder imports
from spyder.plugins.preferences.widgets.configdialog import ConfigDialog

# Local imports
from spyder_notebook.confpage import NotebookConfigPage
from spyder_notebook.tests.test_plugin import plugin_no_server


def test_config(plugin_no_server, qtbot):
    """Test that config page can be created and shown."""
    dlg = ConfigDialog()
    page = NotebookConfigPage(plugin_no_server, parent=plugin_no_server.main)
    page.initialize()
    dlg.add_page(page)
    dlg.show()
    qtbot.addWidget(dlg)
    # no assert, just check that the config page can be created


if __name__ == "__main__":
    pytest.main()
