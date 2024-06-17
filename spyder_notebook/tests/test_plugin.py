# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for the plugin."""

# Standard library imports
import collections
import json
import os
import os.path as osp
from unittest.mock import Mock

# Third-party library imports
from flaky import flaky
import pytest
from qtpy.QtWebEngineWidgets import WEBENGINE
from qtpy.QtWidgets import QMainWindow
import requests

# Spyder imports
from spyder.api.plugins import Plugins
from spyder.config.manager import CONF

# Local imports
from spyder_notebook.notebookplugin import NotebookPlugin

# =============================================================================
# Constants
# =============================================================================
NOTEBOOK_UP = 40000
CALLBACK_TIMEOUT = 10000
LOCATION = osp.realpath(osp.join(os.getcwd(), osp.dirname(__file__)))


# =============================================================================
# Utility functions
# =============================================================================
def prompt_present(nbwidget, qtbot):
    """Check if an In prompt is present in the notebook."""
    return text_present(nbwidget, qtbot, '[ ]:')


def text_present(nbwidget, qtbot, text="Test"):
    """Check if a text is present in the notebook."""
    if WEBENGINE:
        with qtbot.waitCallback(timeout=CALLBACK_TIMEOUT) as cb:
            nbwidget.dom.toHtml(cb)
        return text in cb.args[0]
    else:
        return text in nbwidget.dom.toHtml()


def is_kernel_up(kernel_id, sessions_url):
    """Determine if the kernel with the id is up."""
    sessions_req = requests.get(sessions_url).content.decode()
    sessions = json.loads(sessions_req)

    kernel = False
    for session in sessions:
        if kernel_id == session['kernel']['id']:
            kernel = True
            break

    return kernel


# =============================================================================
# Fixtures
# =============================================================================
class MainMock(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main = self
        self.resize(640, 480)

    def get_plugin(self, plugin_name, error=True):
        return Mock()


@pytest.fixture
def notebook(qtbot):
    """Set up the Notebook plugin with a welcome tab and a tab with a new
    notebook. The latter tab is selected."""
    window = MainMock()
    notebook_plugin = NotebookPlugin(parent=window, configuration=CONF)
    notebook_plugin.get_widget().tabwidget.maybe_create_welcome_client()
    notebook_plugin.get_widget().create_new_client()
    window.setCentralWidget(notebook_plugin.get_widget())
    window.show()

    qtbot.addWidget(window)
    yield notebook_plugin
    notebook_plugin.get_widget().close()


@pytest.fixture
def plugin_no_server(mocker, qtbot):
    """Set up the Notebook plugin with a fake nbopen which does not start
    a notebook server."""
    def fake_get_server(filename, interpreter, start):
        return collections.defaultdict(
            str, filename=filename, root_dir=osp.dirname(filename))
    fake_server_manager = mocker.Mock(get_server=fake_get_server)
    mocker.patch('spyder_notebook.widgets.main_widget.ServerManager',
                 return_value=fake_server_manager)

    window = MainMock()
    plugin = NotebookPlugin(parent=window, configuration=CONF)
    window.show()

    qtbot.addWidget(window)
    yield plugin
    plugin.get_widget().close()


# =============================================================================
# Tests
# =============================================================================

def test_on_mainwindow_visible_with_opened_notebooks(plugin_no_server):
    """
    Run .on_mainwindow_visible() with the `opened_notebooks` conf option set to
    a non-empty list. Check that plugin opens those notebooks.
    """
    plugin = plugin_no_server
    plugin.set_conf('opened_notebooks', ['ham.ipynb', 'spam.ipynb'])

    plugin.on_mainwindow_visible()

    tabwidget = plugin.get_widget().tabwidget
    assert tabwidget.count() == 2
    assert tabwidget.widget(0).filename == 'ham.ipynb'
    assert tabwidget.widget(1).filename == 'spam.ipynb'


def test_on_mainwindow_visible_with_opened_notebooks_empty(plugin_no_server):
    """
    Run .on_mainwindow_visible() with the `opened_notebooks` conf option set to
    an empty list. Check that plugin opens a welcome tab and a new notebook,
    and that the welcome tab is on top.
    """
    plugin = plugin_no_server
    plugin.set_conf('opened_notebooks', [])

    plugin.on_mainwindow_visible()

    tabwidget = plugin.get_widget().tabwidget
    assert tabwidget.count() == 2
    assert tabwidget.is_welcome_client(tabwidget.widget(0))
    assert tabwidget.is_newly_created(tabwidget.widget(1))
    assert tabwidget.currentIndex() == 0


def test_closing_main_widget(mocker, plugin_no_server):
    """Close the main widget with a welcome tab, a new notebooks and a notebook
    opened from a file. Check that config variables `recent_notebooks` and
    `opened_notebook` are correctly set."""
    plugin = plugin_no_server
    main_widget = plugin.get_widget()
    main_widget.clear_recent_notebooks()
    mock_set_option = mocker.patch.object(main_widget, 'set_conf')
    main_widget.tabwidget.maybe_create_welcome_client()
    main_widget.create_new_client()
    main_widget.open_notebook(['ham.ipynb'])

    plugin.get_widget().close()

    expected = [mocker.call('recent_notebooks', ['ham.ipynb']),
                mocker.call('opened_notebooks', ['ham.ipynb'])]
    assert mock_set_option.call_args_list == expected


def test_view_server_info(mocker, plugin_no_server):
    """Check that the "server info" action shows a dialog window with the
    server data."""
    plugin = plugin_no_server
    mock_ServerInfoDialog = mocker.patch(
        'spyder_notebook.widgets.main_widget.ServerInfoDialog')

    plugin.get_widget().server_info_action.trigger()

    mock_ServerInfoDialog.assert_called_once_with(
        plugin.get_widget().server_manager.servers, parent=plugin.get_widget())
    mock_ServerInfoDialog.return_value.show.assert_called_once()


@pytest.mark.parametrize('config_value', ['same as spyder', 'dark', 'light'])
@pytest.mark.parametrize('spyder_is_dark', [True, False])
def test_dark_theme(mocker, plugin_no_server, config_value, spyder_is_dark):
    plugin_no_server.set_conf('theme', config_value)
    mocker.patch('spyder_notebook.widgets.main_widget.is_dark_interface',
                 return_value=spyder_is_dark)

    value = plugin_no_server.get_widget().dark_theme

    expected = (config_value == 'dark' or
                (config_value == 'same as spyder' and spyder_is_dark))
    assert value == expected


if __name__ == "__main__":
    pytest.main()
