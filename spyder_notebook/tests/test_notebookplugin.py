# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""
Tests for notebookplugin.py
"""

# Test library imports
import pytest

# Local imports
from spyder_notebook.notebookplugin import NotebookPlugin

@pytest.fixture
def setup_notebookplugin(qtbot):
    """Set up the notebookplugin."""
    notebook = NotebookPlugin(None)
    notebook.create_new_client()
    qtbot.addWidget(notebook)
    return notebook

def test_notebookplugin(qtbot):
    """Run the notebookplugin."""
    notebook = setup_notebookplugin(qtbot)
    assert notebook
    assert len(notebook.clients) == 1

def test_notebookplugin_create_new_client(qtbot):
    """Create a new client."""
    notebook = setup_notebookplugin(qtbot)
    notebook.create_new_client()
    assert len(notebook.clients) == 2


if __name__ == "__main__":
    pytest.main()
