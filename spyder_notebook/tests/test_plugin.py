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
import pytest
import requests
from qtpy.QtWebEngineWidgets import WEBENGINE
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QFileDialog, QApplication

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
            return 'In&nbsp;[&nbsp;]:' in html
        except NameError:
            return False
    else:
        return 'In&nbsp;[&nbsp;]:' in nbwidget.dom.toHtml()

def get_innerHTML(nbwidget, className):
    """Get the innerHTML of the first element with the given className in the notebook."""
    return nbwidget.evaluate("""
            (function () {{
                var element = document.getElementsByClassName({0})[0];
                return element.innerHTML;
            }})();
            """.format(repr(className)))

def manage_save_dialog(qtbot, directory=LOCATION):
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
            w.accept()

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

@pytest.fixture
def setup_notebook(qtbot):
    """Set up the Notebook plugin."""
    notebook = NotebookPlugin(None)
    qtbot.addWidget(notebook)
    notebook.create_new_client()
    notebook.show()
    return notebook

def test_shutdown_notebook_kernel(qtbot):
    """Test that the kernel is shutdown from the server when closing a notebook."""
    # Create notebook
    notebook = setup_notebook(qtbot)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Get kernel id for the client
    kernel_id, sessions_url = get_kernel_id(notebook.get_current_client())

    # Close the current client
    notebook.close_client()

    # Assert that the kernel is down for the closed client
    assert not is_kernel_up(kernel_id, sessions_url)

def test_open_notebook(qtbot):
    """Test that a notebook can be opened from a non-ascii directory."""
    # Move the test file to non-ascii directory
    test_notebook = osp.join(LOCATION, 'test.ipynb')
    test_notebook_non_ascii = osp.join(LOCATION, 'äöüß', 'test.ipynb')
    os.mkdir(os.path.join(LOCATION, 'äöüß'))
    os.rename(test_notebook, test_notebook_non_ascii)

    # Create notebook
    notebook = setup_notebook(qtbot)

    # Wait for prompt
    notebook.open_notebook(filenames=[test_notebook_non_ascii])
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "Test" in it
    # and the client has the correct name
    assert "Test" in get_innerHTML(nbwidget, "CodeMirror-line")
    assert notebook.get_current_client().get_short_name() == "test.ipynb"

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
    QTimer.singleShot(1000, lambda: manage_save_dialog(qtbot))
    notebook.save_as(name=name)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "test" in it
    # and the client has the correct name
    assert "test" in get_innerHTML(nbwidget, "CodeMirror-line")
    assert notebook.get_current_client().get_short_name() == "save.ipynb"

def test_new_notebook(qtbot):
    """Test that a new client is really a notebook."""
    # Create notebook
    notebook = setup_notebook(qtbot)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that we have one notebook
    assert len(notebook.clients) == 1


if __name__ == "__main__":
    pytest.main()
