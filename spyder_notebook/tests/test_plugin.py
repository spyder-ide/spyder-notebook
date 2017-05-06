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

# Notebook imports
from notebook.utils import url_path_join

# Local imports
from spyder_notebook.notebookplugin import NotebookPlugin


NOTEBOOK_UP = 5000
INTERACTION_CLICK = 100
LOCATION = osp.realpath(osp.join(os.getcwd(), osp.dirname(__file__)))


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

def get_kernel_id(client):
    """Get the kernel id for a client and the sessions url."""
    sessions_url = client.add_token(url_path_join(client.server_url,
                                                  'api/sessions'))
    sessions_req = requests.get(sessions_url).content.decode()
    sessions = json.loads(sessions_req)

    if os.name == 'nt':
        path = client.path.replace('\\', '/')
    else:
        path = client.path

    for session in sessions:
        if session['notebook']['path'] == path:
            kernel_id = session['kernel']['id']
            return (kernel_id, sessions_url)

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

def hidden_class_header(nbwidget):
    """Determine if 'hidden' class of the header is present."""
    element_class = nbwidget.evaluate("""
            (function () {
                var element_class = document.querySelector('#header-container').className;
                return element_class;
            })();
        """)
    return element_class == "hidden"

@pytest.fixture
def setup_notebook(qtbot):
    """Set up the Notebook plugin."""
    notebook = NotebookPlugin(None)
    qtbot.addWidget(notebook)
    notebook.create_new_client()
    notebook.show()
    return notebook

@flaky(max_runs=3)
def test_hide_header(qtbot):
    """Test that the kernel header is hidden."""
    # Create notebook
    notebook = setup_notebook(qtbot)

     # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Wait for hide header
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: hidden_class_header(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that the header is hidden
    assert hidden_class_header(nbwidget)

@flaky(max_runs=3)
def test_shutdown_notebook_kernel(qtbot):
    """Test that the kernel is shutdown from the server when closing a notebook."""
    # Create notebook
    notebook = setup_notebook(qtbot)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Get kernel id for the client
    qtbot.waitUntil(lambda: get_kernel_id(notebook.get_current_client()) is not None, timeout=NOTEBOOK_UP)
    kernel_id, sessions_url = get_kernel_id(notebook.get_current_client())

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
    assert notebook.get_current_client().get_short_name() == "test.ipynb"

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
    assert notebook.get_current_client().get_short_name() == "save.ipynb"

@flaky(max_runs=3)
def test_new_notebook(qtbot):
    """Test that a new client is really a notebook."""
    # Create notebook
    notebook = setup_notebook(qtbot)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that we have one notebook
    assert len(notebook.clients) == 1

@flaky(max_runs=3)
def test_fileswitcher(qtbot):
    """Test the fileswithcher."""
    # Create notebook
    notebook = setup_notebook(qtbot)

    # Create new notebook
    notebook.create_new_client()

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that we have two notebooks
    assert len(notebook.clients) == 2

    # Fileswitcher of the notebook
    notebook.open_fileswitcher_dlg()
    fileswitcher = notebook.fileswitcher_dlg

    # Search for the first untitled0 notebook
    fileswitcher.edit.setText("0")
    
    # Assert that we are at the first notebook
    assert notebook.tabwidget.currentIndex() == 0
    assert notebook.get_current_client().get_short_name() == 'untitled0.ipynb'

    # Search for the untitled1 notebook
    fileswitcher.edit.setText("1")

    # Assert that we are at the first notebook
    assert notebook.tabwidget.currentIndex() == 1
    assert notebook.get_current_client().get_short_name() == 'untitled1.ipynb'

    # Assert that the fileswitcher dialog hides
    qtbot.keyPress(fileswitcher.edit, Qt.Key_Enter)
    qtbot.waitUntil(lambda: not fileswitcher.isVisible(), timeout=NOTEBOOK_UP)
    assert not fileswitcher.isVisible()


if __name__ == "__main__":
    pytest.main()
