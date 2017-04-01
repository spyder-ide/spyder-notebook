# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for the plugin."""

# Test library imports
import pytest
from qtpy.QtWebEngineWidgets import WEBENGINE
from qtpy.QtCore import Qt

# Local imports
from spyder_notebook.notebookplugin import NotebookPlugin


NOTEBOOK_UP = 5000


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


@pytest.fixture
def setup_notebook(qtbot):
    """Set up the Notebook plugin."""
    notebook = NotebookPlugin(None)
    qtbot.addWidget(notebook)
    notebook.create_new_client()
    notebook.show()
    return notebook


def test_new_notebook(qtbot):
    """Test that a new client is really a notebook."""
    # Create notebook
    notebook = setup_notebook(qtbot)

    # Wait for prompt
    nbwidget = notebook.get_current_nbwidget()
    qtbot.waitUntil(lambda: prompt_present(nbwidget), timeout=NOTEBOOK_UP)

    # Assert that we have one notebook
    assert len(notebook.clients) == 1


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
