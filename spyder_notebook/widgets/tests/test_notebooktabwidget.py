# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License

"""Tests for notebooktabwidget.py."""

# Standard library imports
import collections

# Third party imports
import pytest

# Local imports
from spyder_notebook.widgets.notebooktabwidget import NotebookTabWidget


@pytest.fixture
def tabwidget(mocker, qtbot):
    """Create an empty NotebookTabWidget which does not start up servers."""
    mocker.patch('spyder_notebook.widgets.notebooktabwidget.nbopen',
                 return_value=collections.defaultdict(str))
    widget = NotebookTabWidget(None)
    qtbot.addWidget(widget)
    return widget


def test_is_newly_created_with_new_notebook(tabwidget):
    """Test that .is_newly_created() returns True if passed a client that is
    indeed newly created."""
    client = tabwidget.create_new_client()
    assert tabwidget.is_newly_created(client)


def test_is_newly_created_with_opened_notebook(tabwidget):
    """Test that .is_newly_created() returns False if passed a client that
    contains a notebook opened from a file."""
    client = tabwidget.create_new_client('ham.ipynb')
    assert not tabwidget.is_newly_created(client)


def test_is_newly_created_with_welcome_tab(tabwidget):
    """Test that .is_newly_created() returns False if passed a welcome
    client."""
    client = tabwidget.maybe_create_welcome_client()
    assert not tabwidget.is_newly_created(client)


def test_is_welcome_client_with_new_notebook(tabwidget):
    """Test that .is_welcome_client() returns False if passed a client that is
    indeed newly created."""
    client = tabwidget.create_new_client()
    assert not tabwidget.is_welcome_client(client)


def test_is_welcome_client_with_opened_notebook(tabwidget):
    """Test that .is_welcome_client() returns False if passed a client that
    contains a notebook opened from a file."""
    client = tabwidget.create_new_client('ham.ipynb')
    assert not tabwidget.is_welcome_client(client)


def test_is_welcome_client_with_welcome_tab(tabwidget):
    """Test that .is_welcome_client() returns True if passed a welcome
    client."""
    client = tabwidget.maybe_create_welcome_client()
    assert tabwidget.is_welcome_client(client)
