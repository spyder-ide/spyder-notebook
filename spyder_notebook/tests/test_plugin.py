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
import shutil
import sys
from unittest.mock import Mock

# Third-party library imports
from flaky import flaky
import pytest
import requests
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWebEngineWidgets import WEBENGINE
from qtpy.QtWidgets import QFileDialog, QApplication, QLineEdit, QMainWindow

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
INTERACTION_CLICK = 100
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


def manage_save_dialog(qtbot, fname, directory=LOCATION):
    """
    Manage the QFileDialog when saving.

    You can use this with QTimer to manage the QFileDialog.
    Before calling anything that may show a QFileDialog for save call:
    QTimer.singleShot(1000, lambda: manage_save_dialog(qtbot))
    """
    top_level_widgets = QApplication.topLevelWidgets()
    for w in top_level_widgets:
        if isinstance(w, QFileDialog):
            if directory is not None:
                w.setDirectory(directory)
            input_field = w.findChildren(QLineEdit)[0]
            input_field.setText(fname)
            qtbot.keyClick(w, Qt.Key_Enter)


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
        self.switcher = Mock()
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
            str, filename=filename, notebook_dir=osp.dirname(filename))
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
@flaky(max_runs=3)
def test_shutdown_notebook_kernel(notebook, qtbot):
    """Test that kernel is shutdown from server when closing a notebook."""
    # Wait for prompt
    nbwidget = notebook.get_widget().tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Get kernel id for the client
    client = notebook.get_widget().tabwidget.currentWidget()
    qtbot.waitUntil(lambda: client.get_kernel_id() is not None,
                    timeout=NOTEBOOK_UP)
    kernel_id = client.get_kernel_id()
    sessions_url = client.get_session_url()

    # Close the current client
    notebook.get_widget().tabwidget.close_client()

    # Assert that the kernel is down for the closed client
    assert not is_kernel_up(kernel_id, sessions_url)


def test_file_in_temp_dir_deleted_after_notebook_closed(notebook, qtbot):
    """Test that notebook file in temporary directory is deleted after the
    notebook is closed."""
    # Wait for prompt
    nbwidget = notebook.get_widget().tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Get file name
    client = notebook.get_widget().tabwidget.currentWidget()
    filename = client.get_filename()

    # Close the current client
    notebook.get_widget().tabwidget.close_client()

    # Assert file is deleted
    assert not osp.exists(filename)


def test_close_nonexisting_notebook(notebook, qtbot):
    """Test that we can close a tab if the notebook file does not exist.
    Regression test for spyder-ide/spyder-notebook#187."""
    # Set up tab with non-existingg notebook
    filename = osp.join(LOCATION, 'does-not-exist.ipynb')
    notebook.open_notebook(filenames=[filename])
    nbwidget = notebook.get_widget().tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)
    client = notebook.get_widget().tabwidget.currentWidget()

    # Close tab
    notebook.get_widget().tabwidget.close_client()

    # Assert tab is closed (without raising an exception)
    for client_index in range(notebook.get_widget().tabwidget.count()):
        assert client != notebook.get_widget().tabwidget.widget(client_index)


# TODO Find out what goes wrong on Mac
@flaky(max_runs=3)
@pytest.mark.skipif(sys.platform == 'darwin', reason='Prompt never comes up')
def test_open_notebook_in_non_ascii_dir(notebook, qtbot, tmpdir):
    """Test that a notebook can be opened from a non-ascii directory."""
    # Move the test file to non-ascii directory
    test_notebook = osp.join(LOCATION, 'test.ipynb')
    test_notebook_non_ascii = osp.join(str(tmpdir), u'äöüß', 'test.ipynb')
    os.mkdir(os.path.join(str(tmpdir), u'äöüß'))
    shutil.copyfile(test_notebook, test_notebook_non_ascii)

    # Wait for prompt
    notebook.open_notebook(filenames=[test_notebook_non_ascii])
    nbwidget = notebook.get_widget().tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "Test" in it
    # and the client has the correct name
    qtbot.waitUntil(lambda: text_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)
    assert text_present(nbwidget, qtbot)
    assert notebook.get_widget().tabwidget.currentWidget().get_short_name() ==\
           "test"


@flaky(max_runs=3)
@pytest.mark.skipif(not sys.platform.startswith('linux'),
                    reason='Test hangs on CI on Windows and MacOS')
def test_save_notebook(notebook, qtbot, tmpdir):
    """Test that a notebook can be saved."""
    # Wait for prompt
    nbwidget = notebook.get_widget().tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Writes: a = "test"
    qtbot.keyClick(nbwidget, Qt.Key_A, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_Space, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_Equal, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_Space, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_QuoteDbl, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_T, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_E, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_S, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_T, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_QuoteDbl, delay=INTERACTION_CLICK)

    # Save the notebook
    name = osp.join(str(tmpdir), 'save.ipynb')
    QTimer.singleShot(1000, lambda: manage_save_dialog(qtbot, fname=name))
    notebook.get_widget().save_as()

    # Wait for prompt
    nbwidget = notebook.get_widget().tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "test" in it
    # and the client has the correct name
    qtbot.waitUntil(lambda: text_present(nbwidget, qtbot, text="test"),
                    timeout=NOTEBOOK_UP)
    assert text_present(nbwidget, qtbot, text="test")
    assert notebook.get_widget().tabwidget.currentWidget().get_short_name() ==\
           "save"


def test_save_notebook_as_with_error(mocker, notebook, qtbot, tmpdir):
    """Test that errors are handled in save_as()."""
    # Set up mocks
    name = osp.join(str(tmpdir), 'save.ipynb')
    mocker.patch('spyder_notebook.widgets.notebooktabwidget.getsavefilename',
                 return_value=(name, 'ignored'))
    mocker.patch('spyder_notebook.widgets.notebooktabwidget.nbformat.write',
                 side_effect=PermissionError)
    mock_critical = mocker.patch('spyder_notebook.widgets.notebooktabwidget'
                                 '.QMessageBox.critical')

    # Wait for prompt
    nbwidget = notebook.get_widget().tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Save the notebook
    notebook.get_widget().save_as()

    # Assert that message box is displayed (reporting error raised by write)
    assert mock_critical.called


@flaky(max_runs=3)
def test_new_notebook(notebook, qtbot):
    """Test that a new client is really a notebook."""
    # Wait for prompt
    nbwidget = notebook.get_widget().tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Assert that we have one notebook and the welcome page
    assert notebook.get_widget().tabwidget.count() == 2


# Teardown sometimes fails on Mac with Python 3.8 due to NoProcessException
# in shutdown_server() in notebookapp.py in external notebook library
@flaky
def test_open_console_when_no_kernel(notebook, qtbot, mocker):
    """Test that open_console() handles the case when there is no kernel."""
    # Create mock IPython console plugin and QMessageBox
    MockMessageBox = mocker.patch(
        'spyder_notebook.widgets.main_widget.QMessageBox')

    # Wait for prompt
    nbwidget = notebook.get_widget().tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Shut the kernel down and check that this is successful
    client = notebook.get_widget().tabwidget.currentWidget()
    kernel_id = client.get_kernel_id()
    sessions_url = client.get_session_url()
    client.shutdown_kernel()
    assert not is_kernel_up(kernel_id, sessions_url)

    # Try opening a console
    notebook.get_widget().open_console(client)

    # Assert that a dialog is displayed and no console was opened
    MockMessageBox.critical.assert_called()
    ipyconsole = notebook.get_plugin(Plugins.IPythonConsole)
    ipyconsole._create_client_for_kernel.assert_not_called()


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
