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

# Third-party library imports
from flaky import flaky
import pytest
import requests
from qtpy.QtWebEngineWidgets import WEBENGINE
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QFileDialog, QApplication, QLineEdit

# Local imports
from spyder_notebook.notebookplugin import NotebookPlugin

# =============================================================================
# Constants
# =============================================================================
NOTEBOOK_UP = 40000
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
        with qtbot.waitCallback() as cb:
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
@pytest.fixture
def notebook(qtbot):
    """Set up the Notebook plugin with a welcome tab and a tab with a new
    notebook. The latter tab is selected."""
    notebook_plugin = NotebookPlugin(None, testing=True)
    qtbot.addWidget(notebook_plugin)
    notebook_plugin.tabwidget.maybe_create_welcome_client()
    notebook_plugin.create_new_client()
    yield notebook_plugin
    notebook_plugin.closing_plugin()


@pytest.fixture
def plugin_no_server(mocker, qtbot):
    """Set up the Notebook plugin with a fake nbopen which does not start
    a notebook server."""
    def fake_get_server(filename, start):
        return collections.defaultdict(
            str, filename=filename, notebook_dir=osp.dirname(filename))
    fake_server_manager = mocker.Mock(get_server=fake_get_server)
    mocker.patch('spyder_notebook.notebookplugin.ServerManager',
                 return_value=fake_server_manager)
    plugin = NotebookPlugin(None, testing=True)
    plugin.main = mocker.Mock()
    qtbot.addWidget(plugin)
    yield plugin
    plugin.closing_plugin()

# =============================================================================
# Tests
# =============================================================================
@flaky(max_runs=3)
def test_shutdown_notebook_kernel(notebook, qtbot):
    """Test that kernel is shutdown from server when closing a notebook."""
    # Wait for prompt
    nbwidget = notebook.tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Get kernel id for the client
    client = notebook.tabwidget.currentWidget()
    qtbot.waitUntil(lambda: client.get_kernel_id() is not None,
                    timeout=NOTEBOOK_UP)
    kernel_id = client.get_kernel_id()
    sessions_url = client.get_session_url()

    # Close the current client
    notebook.tabwidget.close_client()

    # Assert that the kernel is down for the closed client
    assert not is_kernel_up(kernel_id, sessions_url)


def test_file_in_temp_dir_deleted_after_notebook_closed(notebook, qtbot):
    """Test that notebook file in temporary directory is deleted after the
    notebook is closed."""
    # Wait for prompt
    nbwidget = notebook.tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Get file name
    client = notebook.tabwidget.currentWidget()
    filename = client.get_filename()

    # Close the current client
    notebook.tabwidget.close_client()

    # Assert file is deleted
    assert not osp.exists(filename)


def test_close_nonexisting_notebook(notebook, qtbot):
    """Test that we can close a tab if the notebook file does not exist.
    Regression test for spyder-ide/spyder-notebook#187."""
    # Set up tab with non-existingg notebook
    filename = osp.join(LOCATION, 'does-not-exist.ipynb')
    notebook.open_notebook(filenames=[filename])
    nbwidget = notebook.tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)
    client = notebook.tabwidget.currentWidget()

    # Close tab
    notebook.tabwidget.close_client()

    # Assert tab is closed (without raising an exception)
    for client_index in range(notebook.tabwidget.count()):
        assert client != notebook.tabwidget.widget(client_index)


@flaky(max_runs=3)
def test_open_notebook(notebook, qtbot, tmpdir):
    """Test that a notebook can be opened from a non-ascii directory."""
    # Move the test file to non-ascii directory
    test_notebook = osp.join(LOCATION, 'test.ipynb')
    test_notebook_non_ascii = osp.join(str(tmpdir), u'äöüß', 'test.ipynb')
    os.mkdir(os.path.join(str(tmpdir), u'äöüß'))
    shutil.copyfile(test_notebook, test_notebook_non_ascii)

    # Wait for prompt
    notebook.open_notebook(filenames=[test_notebook_non_ascii])
    nbwidget = notebook.tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "Test" in it
    # and the client has the correct name
    qtbot.waitUntil(lambda: text_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)
    assert text_present(nbwidget, qtbot)
    assert notebook.tabwidget.currentWidget().get_short_name() == "test"


@flaky(max_runs=3)
@pytest.mark.skipif(not sys.platform.startswith('linux'),
                    reason='Test hangs on CI on Windows and MacOS')
def test_save_notebook(notebook, qtbot, tmpdir):
    """Test that a notebook can be saved."""
    # Wait for prompt
    nbwidget = notebook.tabwidget.currentWidget().notebookwidget
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
    notebook.save_as()

    # Wait for prompt
    nbwidget = notebook.tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "test" in it
    # and the client has the correct name
    qtbot.waitUntil(lambda: text_present(nbwidget, qtbot, text="test"),
                    timeout=NOTEBOOK_UP)
    assert text_present(nbwidget, qtbot, text="test")
    assert notebook.tabwidget.currentWidget().get_short_name() == "save"


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
    nbwidget = notebook.tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Save the notebook
    notebook.save_as()

    # Assert that message box is displayed (reporting error raised by write)
    assert mock_critical.called


@flaky(max_runs=3)
def test_new_notebook(notebook, qtbot):
    """Test that a new client is really a notebook."""
    # Wait for prompt
    nbwidget = notebook.tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Assert that we have one notebook and the welcome page
    assert notebook.tabwidget.count() == 2


def test_open_console_when_no_kernel(notebook, qtbot, mocker):
    """Test that open_console() handles the case when there is no kernel."""
    # Create mock IPython console plugin and QMessageBox
    notebook.ipyconsole = mocker.Mock()
    MockMessageBox = mocker.patch('spyder_notebook.notebookplugin.QMessageBox')

    # Wait for prompt
    nbwidget = notebook.tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Shut the kernel down and check that this is successful
    client = notebook.tabwidget.currentWidget()
    kernel_id = client.get_kernel_id()
    sessions_url = client.get_session_url()
    client.shutdown_kernel()
    assert not is_kernel_up(kernel_id, sessions_url)

    # Try opening a console
    notebook.open_console(client)

    # Assert that a dialog is displayed and no console was opened
    MockMessageBox.critical.assert_called()
    notebook.ipyconsole._create_client_for_kernel.assert_not_called()


def test_register_plugin_with_opened_notebooks(mocker, plugin_no_server):
    """Run .register_plugin() with the `opened_notebooks` conf option set to
    a non-empty list. Check that plugin opens those notebooks."""
    plugin = plugin_no_server
    plugin.set_option('opened_notebooks', ['ham.ipynb', 'spam.ipynb'])

    plugin.register_plugin()

    tabwidget = plugin.tabwidget
    assert tabwidget.count() == 2
    assert tabwidget.widget(0).filename == 'ham.ipynb'
    assert tabwidget.widget(1).filename == 'spam.ipynb'


def test_register_plugin_with_opened_notebooks_empty(mocker, plugin_no_server):
    """Run .register_plugin() with the `opened_notebooks` conf option set to
    an empty list. Check that plugin opens a welcome tab and a new notebook,
    and that the welcome tab is on top."""
    plugin = plugin_no_server
    plugin.set_option('opened_notebooks', [])

    plugin.register_plugin()

    tabwidget = plugin.tabwidget
    assert tabwidget.count() == 2
    assert tabwidget.is_welcome_client(tabwidget.widget(0))
    assert tabwidget.is_newly_created(tabwidget.widget(1))
    assert tabwidget.currentIndex() == 0


def test_closing_plugin(mocker, plugin_no_server):
    """Close a plugin with a welcome tab, a new notebooks and a notebook
    opened from a file. Check that config variables `recent_notebooks` and
    `opened_notebook` are correctly set."""
    plugin = plugin_no_server
    plugin.clear_recent_notebooks()
    mock_set_option = mocker.patch.object(plugin, 'set_option')
    plugin.tabwidget.maybe_create_welcome_client()
    plugin.create_new_client()
    plugin.open_notebook(['ham.ipynb'])

    plugin.closing_plugin()

    expected = [mocker.call('recent_notebooks', ['ham.ipynb']),
                mocker.call('opened_notebooks', ['ham.ipynb'])]
    assert mock_set_option.call_args_list == expected


if __name__ == "__main__":
    pytest.main()
