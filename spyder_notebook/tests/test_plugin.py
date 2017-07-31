# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for the plugin."""

# Standard library imports
import os
import os.path as osp
import json

# Third-party library imports
from flaky import flaky
import pytest
import requests
from qtpy.QtWebEngineWidgets import WEBENGINE
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QFileDialog, QApplication, QLineEdit

# Local imports
from spyder_notebook.notebookplugin import NotebookPlugin


#==============================================================================
# Constants
#==============================================================================
NOTEBOOK_UP = 5000
INTERACTION_CLICK = 100
LOCATION = osp.realpath(osp.join(os.getcwd(), osp.dirname(__file__)))


#==============================================================================
# Utility functions
#==============================================================================
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


#==============================================================================
# Fixtures
#==============================================================================
@pytest.fixture
def setup_notebook(qtbot):
    """Set up the Notebook plugin."""
    notebook = NotebookPlugin(None, testing=True)
    qtbot.addWidget(notebook)
    notebook.create_new_client()
    notebook.show()
    return notebook


#==============================================================================
# Tests
#==============================================================================
@flaky(max_runs=3)
def test_hide_header(qtbot):
    """Test that the kernel header is hidden."""
    # Create notebook
    notebook = setup_notebook(qtbot)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Wait for hide header
    qtbot.waitUntil(lambda: text_present(nbwidget,
                                         'id="header-container" class="hidden"'),
                    timeout=NOTEBOOK_UP)

    # Assert that the header is hidden
    assert text_present(nbwidget, 'id="header-container" class="hidden"')


@flaky(max_runs=3)
def test_shutdown_notebook_kernel(qtbot):
    """Test that the kernel is shutdown from the server when closing a notebook."""
    # Create notebook
    notebook = setup_notebook(qtbot)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Get kernel id for the client
    client = notebook.get_current_client()
    qtbot.waitUntil(lambda: client.get_kernel_id() is not None, timeout=NOTEBOOK_UP)
    kernel_id = client.get_kernel_id()
    sessions_url = client.get_session_url()

    # Close the current client
    notebook.close_client()

    # Assert that the kernel is down for the closed client
    assert not is_kernel_up(kernel_id, sessions_url)


@flaky(max_runs=3)
def test_open_notebook(qtbot):
    """Test that a notebook can be opened from a non-ascii directory."""
    # Move the test file to non-ascii directory
    test_notebook = osp.join(LOCATION, 'test.ipynb')
    test_notebook_non_ascii = osp.join(LOCATION, u'äöüß', 'test.ipynb')
    os.mkdir(os.path.join(LOCATION, u'äöüß'))
    os.rename(test_notebook, test_notebook_non_ascii)

    # Create notebook
    notebook = setup_notebook(qtbot)

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
def test_save_notebook(qtbot):
    """Test that a notebook can be saved."""
    # Create notebook
    notebook = setup_notebook(qtbot)

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
    name = 'save.ipynb'
    QTimer.singleShot(1000, lambda: manage_save_dialog(qtbot, fname=name))
    notebook.save_as(name=name)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "test" in it
    # and the client has the correct name
    qtbot.waitUntil(lambda: text_present(nbwidget, text="test"), timeout=NOTEBOOK_UP)
    assert text_present(nbwidget, text="test")
    assert notebook.get_current_client().get_short_name() == "save"


@flaky(max_runs=3)
def test_new_notebook(qtbot):
    """Test that a new client is really a notebook."""
    # Create notebook
    notebook = setup_notebook(qtbot)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that we have one notebook and the welcome page
    assert len(notebook.clients) == 2


if __name__ == "__main__":
    pytest.main()
