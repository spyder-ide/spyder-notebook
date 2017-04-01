# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for the plugin."""

# Standard library imports
import os
import os.path as osp

# Test library imports
import pytest
from qtpy.QtWebEngineWidgets import WEBENGINE
from qtpy.QtCore import Qt

# Local imports
from spyder_notebook.notebookplugin import NotebookPlugin


NOTEBOOK_UP = 5000
INTERACTION_CLICK = 500
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

@pytest.fixture
def setup_notebook(qtbot):
    """Set up the Notebook plugin."""
    notebook = NotebookPlugin(None)
    qtbot.addWidget(notebook)
    notebook.create_new_client()
    notebook.show()
    return notebook

def test_open_notebook(qtbot):
    """Test that a netbook can be opened from a non-ascii directory."""
    # Move the test file to non-ascii directory
    test_notebook = osp.join(LOCATION, 'test.ipynb')
    test_notebook_ascii = osp.join(LOCATION, 'á', 'test.ipynb')
    os.mkdir(os.path.join(LOCATION, 'á'))
    os.rename(test_notebook, test_notebook_ascii)

    # Create notebook
    notebook = setup_notebook(qtbot)

    # Wait for prompt
    notebook.open_notebook(filenames=[test_notebook_ascii])
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "Test" in it
    assert "Test" in get_innerHTML(nbwidget, "CodeMirror-line")

def test_save_notebook(qtbot):
    """Test that a notebook can be saved."""
    # Create notebook
    notebook = setup_notebook(qtbot)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # writes: a = "test"
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
    filename = osp.join(LOCATION, 'saveTest.ipynb')
    notebook.save_as(filename=filename)
    nbwidget = notebook.get_current_nbwidget()

    # Wait for prompt
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "test" in it
    assert "test" in get_innerHTML(nbwidget, "CodeMirror-line")

def test_kill_notebook_kernel(qtbot):
    """Test that the kernel is killed from the server when closing a notebook."""
    # Create notebook
    notebook = setup_notebook(qtbot)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Get kernel id for the client
    kernel_id = "the server info about the id"
    notebook.close_client()

    # Get kernels id for the clients

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
