# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License

"""Tests for notebooktabwidget.py."""

# Standard library imports
import collections
import os.path as osp

# Third party imports
import pytest
from qtpy.QtWidgets import QMessageBox

# Local imports
from spyder_notebook.utils.servermanager import ServerManager
from spyder_notebook.widgets.notebooktabwidget import (
    NotebookTabWidget, WAIT_SAVE_ITERATIONS)


@pytest.fixture
def tabwidget(mocker, qtbot):
    """Create an empty NotebookTabWidget which does not start up servers."""
    def fake_get_server(filename, start):
        return collections.defaultdict(
            str, filename=filename, notebook_dir=osp.dirname(filename))

    mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.WAIT_SAVE_DELAY', 1)
    fake_server_manager = mocker.Mock(
        spec=ServerManager, get_server=fake_get_server)
    widget = NotebookTabWidget(None, fake_server_manager)
    qtbot.addWidget(widget)
    return widget


def test_save_notebook_with_opened_notebook(mocker, tabwidget):
    """Test that .save_notebook() with a notebook opened from a file does
    indeed save the notebook but does not try to read it again."""
    mock_read = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.nbformat.read')
    client = tabwidget.create_new_client('ham.ipynb')
    client.save = mocker.Mock()

    result = tabwidget.save_notebook(client)

    client.save.assert_called()
    mock_read.assert_not_called()
    assert result == 'ham.ipynb'


def test_save_notebook_with_empty_new_notebook(mocker, tabwidget):
    """Test that .save_notebook() on a newly created, empty notebook saves
    the notebook, reads it back again but does not ask to save it again."""
    contents = {'cells': []}
    mock_read = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.nbformat.read',
        return_value=contents)
    mock_question = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.QMessageBox.question')
    client = tabwidget.create_new_client()
    client.save = mocker.Mock()

    result = tabwidget.save_notebook(client)

    client.save.assert_called()
    mock_read.assert_called_once()
    mock_question.assert_not_called()
    assert result.endswith('untitled0.ipynb')


def test_save_notebook_with_nonempty_new_notebook_and_save(mocker, tabwidget):
    """Test that .save_notebook() on a newly created, non-empty notebook saves
    the notebook, reads it back again, asks to save it again, and if yes, does
    save it under a new name."""
    contents = {'cells': [{'source': 'not empty'}]}
    mock_read = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.nbformat.read',
        return_value=contents)
    mock_question = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.QMessageBox.question',
        return_value=QMessageBox.Yes)
    client = tabwidget.create_new_client()
    client.save = mocker.Mock()
    tabwidget.save_as = mocker.Mock(return_value='newname.ipynb')

    result = tabwidget.save_notebook(client)

    client.save.assert_called()
    mock_read.assert_called_once()
    mock_question.assert_called_once()
    tabwidget.save_as.assert_called_once()
    assert result == 'newname.ipynb'


def test_save_notebook_with_nonempty_new_notebook_and_no_save(
            mocker, tabwidget):
    """Test that .save_notebook() on a newly created, non-empty notebook saves
    the notebook, reads it back again, asks to save it again, and if no, does
    not save it under a new name."""
    contents = {'cells': [{'source': 'not empty'}]}
    mock_read = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.nbformat.read',
        return_value=contents)
    mock_question = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.QMessageBox.question',
        return_value=QMessageBox.No)
    client = tabwidget.create_new_client()
    client.save = mocker.Mock()
    tabwidget.save_as = mocker.Mock(return_value='newname.ipynb')

    result = tabwidget.save_notebook(client)

    client.save.assert_called()
    mock_read.assert_called_once()
    mock_question.assert_called_once()
    tabwidget.save_as.assert_not_called()
    assert result.endswith('untitled0.ipynb')


def test_save_notebook_with_empty_new_notebook_and_delay(
            mocker, tabwidget):
    """Test that .save_notebook() on a newly created, empty notebook saves
    the notebook and reads it back again, and when that fails because the file
    does not exists, try again to read it back. When the read succeeds the
    second time and the notebook turns out to be empty, the user is not asked
    to save it again."""
    contents = {'cells': []}
    mock_read = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.nbformat.read',
        side_effect=[FileNotFoundError, contents])
    mock_question = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.QMessageBox.question',
        return_value=QMessageBox.No)
    client = tabwidget.create_new_client()
    client.save = mocker.Mock()
    tabwidget.save_as = mocker.Mock(return_value='newname.ipynb')

    result = tabwidget.save_notebook(client)

    client.save.assert_called()
    assert mock_read.call_count == 2
    mock_question.assert_not_called()
    assert result.endswith('untitled0.ipynb')


def test_save_notebook_with_new_notebook_and_long_delay(mocker, tabwidget):
    """Test that .save_notebook() on a newly created, empty notebook saves
    the notebook and reads it back again, and when that keeps fails because
    the file does not exists, eventually gives up and does not ask to save
    again."""
    mock_read = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.nbformat.read',
        side_effect=FileNotFoundError)
    mock_question = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.QMessageBox.question',
        return_value=QMessageBox.No)
    client = tabwidget.create_new_client()
    client.save = mocker.Mock()
    tabwidget.save_as = mocker.Mock(return_value='newname.ipynb')

    result = tabwidget.save_notebook(client)

    client.save.assert_called()
    assert mock_read.call_count == WAIT_SAVE_ITERATIONS
    mock_question.assert_not_called()
    assert result.endswith('untitled0.ipynb')


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
