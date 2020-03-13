# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for the plugin."""

# Standard library imports
import json
import os
import os.path as osp
import shutil
import sys
import tempfile

# Third-party library imports
from flaky import flaky
import pytest
import requests
from qtpy.QtWebEngineWidgets import WEBENGINE
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QFileDialog, QApplication, QLineEdit
from spyder.config.base import get_home_dir

# Local imports
from spyder_notebook.notebookplugin import NotebookPlugin

# Python 2 compatibility
if sys.version_info[0] == 2:
    PermissionError = OSError

# =============================================================================
# Constants
# =============================================================================
NOTEBOOK_UP = 5000
INTERACTION_CLICK = 100
LOCATION = osp.realpath(osp.join(os.getcwd(), osp.dirname(__file__)))


# =============================================================================
# Utility functions
# =============================================================================
def prompt_present(nbwidget):
    """Check if an In prompt is present in the notebook."""
    if WEBENGINE:
        def callback(data):
            global html
            html = data
        nbwidget.dom.toHtml(callback)
        try:
            return '&nbsp;[&nbsp;]:' in html
        except NameError:
            return False
    else:
        return '&nbsp;[&nbsp;]:' in nbwidget.dom.toHtml()


def text_present(nbwidget, text="Test"):
    """Check if a text is present in the notebook."""
    if WEBENGINE:
        def callback(data):
            global html
            html = data
        nbwidget.dom.toHtml(callback)
        try:
            return text in html
        except NameError:
            return False
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
    """Set up the Notebook plugin."""
    notebook_plugin = NotebookPlugin(None, testing=True)
    qtbot.addWidget(notebook_plugin)
    notebook_plugin.create_new_client()
    return notebook_plugin


@pytest.fixture(scope='module')
def tmpdir_under_home():
    """Create a temporary directory under the home dir."""
    tmpdir = tempfile.mkdtemp(dir=get_home_dir())
    yield tmpdir
    print('rmtree', tmpdir)
    shutil.rmtree(tmpdir)


# =============================================================================
# Tests
# =============================================================================
@flaky(max_runs=3)
def test_hide_header(notebook, qtbot):
    """Test that the kernel header is hidden."""
    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Wait for hide header
    html_fragment = 'id="header-container" class="hidden"'
    qtbot.waitUntil(lambda: text_present(nbwidget, html_fragment),
                    timeout=NOTEBOOK_UP)

    # Assert that the header is hidden
    assert text_present(nbwidget, html_fragment)


@flaky(max_runs=3)
def test_shutdown_notebook_kernel(notebook, qtbot):
    """Test that kernel is shutdown from server when closing a notebook."""
    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Get kernel id for the client
    client = notebook.get_current_client()
    qtbot.waitUntil(lambda: client.get_kernel_id() is not None,
                    timeout=NOTEBOOK_UP)
    kernel_id = client.get_kernel_id()
    sessions_url = client.get_session_url()

    # Close the current client
    notebook.close_client()

    # Assert that the kernel is down for the closed client
    assert not is_kernel_up(kernel_id, sessions_url)


def test_file_in_temp_dir_deleted_after_notebook_closed(notebook, qtbot):
    """Test that notebook file in temporary directory is deleted after the
    notebook is closed."""
    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Get file name
    client = notebook.get_current_client()
    filename = client.get_filename()

    # Close the current client
    notebook.close_client()

    # Assert file is deleted
    assert not osp.exists(filename)


def test_close_nonexisting_notebook(notebook, qtbot):
    """Test that we can close a tab if the notebook file does not exist.
    Regression test for spyder-ide/spyder-notebook#187."""
    # Set up tab with non-existingg notebook
    filename = osp.join(LOCATION, 'does-not-exist.ipynb')
    notebook.open_notebook(filenames=[filename])
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)
    client = notebook.get_current_client()

    # Close tab
    notebook.close_client()

    # Assert tab is closed (without raising an exception)
    assert client not in notebook.clients


@flaky(max_runs=3)
def test_open_notebook(notebook, qtbot, tmpdir_under_home):
    """Test that a notebook can be opened from a non-ascii directory."""
    # Move the test file to non-ascii directory
    test_notebook = osp.join(LOCATION, 'test.ipynb')

    # For Python 2, non-ascii directory needs to be under home dir
    test_notebook_non_ascii = osp.join(tmpdir_under_home,
                                       u'äöüß', 'test.ipynb')
    os.mkdir(os.path.join(tmpdir_under_home, u'äöüß'))
    shutil.copyfile(test_notebook, test_notebook_non_ascii)

    # Wait for prompt
    notebook.open_notebook(filenames=[test_notebook_non_ascii])
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "Test" in it
    # and the client has the correct name
    qtbot.waitUntil(lambda: text_present(nbwidget), timeout=NOTEBOOK_UP)
    assert text_present(nbwidget)
    assert notebook.get_current_client().get_short_name() == "test"


@flaky(max_runs=3)
@pytest.mark.skipif(not sys.platform.startswith('linux'),
                    reason='Test hangs on CI on Windows and MacOS')
def test_save_notebook(notebook, qtbot, tmpdir):
    """Test that a notebook can be saved."""
    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

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
    notebook.save_as(name=name)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "test" in it
    # and the client has the correct name
    qtbot.waitUntil(lambda: text_present(nbwidget, text="test"),
                    timeout=NOTEBOOK_UP)
    assert text_present(nbwidget, text="test")
    assert notebook.get_current_client().get_short_name() == "save"


def test_save_notebook_as_with_error(mocker, notebook, qtbot, tmpdir):
    """Test that errors are handled in save_as()."""
    # Set up mocks
    name = osp.join(str(tmpdir), 'save.ipynb')
    mocker.patch('spyder_notebook.notebookplugin.getsavefilename',
                 return_value=(name, 'ignored'))
    mocker.patch('spyder_notebook.notebookplugin.nbformat.write',
                 side_effect=PermissionError)
    mock_critical = mocker.patch('spyder_notebook.notebookplugin.QMessageBox'
                                 '.critical')

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Save the notebook
    notebook.save_as()

    # Assert that message box is displayed (reporting error raised by write)
    assert mock_critical.called


@flaky(max_runs=3)
def test_new_notebook(notebook, qtbot):
    """Test that a new client is really a notebook."""
    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that we have one notebook and the welcome page
    assert len(notebook.clients) == 2


def test_open_console_when_no_kernel(notebook, qtbot, mocker):
    """Test that open_console() handles the case when there is no kernel."""
    # Create mock IPython console plugin and QMessageBox
    notebook.ipyconsole = mocker.Mock()
    MockMessageBox = mocker.patch('spyder_notebook.notebookplugin.QMessageBox')

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Shut the kernel down and check that this is successful
    client = notebook.get_current_client()
    kernel_id = client.get_kernel_id()
    sessions_url = client.get_session_url()
    client.shutdown_kernel()
    assert not is_kernel_up(kernel_id, sessions_url)

    # Try opening a console
    notebook.open_console(client)

    # Assert that a dialog is displayed and no console was opened
    MockMessageBox.critical.assert_called()
    notebook.ipyconsole._create_client_for_kernel.assert_not_called()


if __name__ == "__main__":
    pytest.main()
