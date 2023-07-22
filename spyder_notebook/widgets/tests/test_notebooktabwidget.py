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
from nbformat.reader import NotJSONError

# Local imports
from spyder_notebook.utils.servermanager import ServerManager
from spyder_notebook.widgets.notebooktabwidget import (
    NotebookTabWidget, WAIT_SAVE_ITERATIONS)


@pytest.fixture
def tabwidget(mocker, qtbot):
    """Create an empty NotebookTabWidget which does not start up servers."""
    def fake_get_server(filename, interpreter, start):
        return collections.defaultdict(
            str, filename=filename, root_dir=osp.dirname(filename))

    mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.WAIT_SAVE_DELAY', 1)
    fake_server_manager = mocker.Mock(
        spec=ServerManager, get_server=fake_get_server)
    widget = NotebookTabWidget(None, fake_server_manager)
    qtbot.addWidget(widget)
    return widget


def test_save_notebook_with_opened_notebook(mocker, tabwidget):
    """Test that .save_notebook() with a notebook opened from a file does
    indeed save the notebook but does not check whether it is empty."""
    client = tabwidget.create_new_client('ham.ipynb')
    client.save = mocker.Mock()
    tabwidget.wait_and_check_if_empty = mocker.Mock()

    result = tabwidget.save_notebook(client)

    client.save.assert_called()
    tabwidget.wait_and_check_if_empty.assert_not_called()
    assert result == 'ham.ipynb'


def test_save_notebook_with_empty_new_notebook(mocker, tabwidget):
    """Test that .save_notebook() on a newly created notebook saves the
    notebook, checks that it is empty, and it is, does not ask to save it
    again."""
    mock_question = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.QMessageBox.question')
    client = tabwidget.create_new_client()
    client.save = mocker.Mock()
    tabwidget.wait_and_check_if_empty = mocker.Mock(return_value=True)

    result = tabwidget.save_notebook(client)

    client.save.assert_called()
    tabwidget.wait_and_check_if_empty.assert_called()
    mock_question.assert_not_called()
    assert result.endswith('untitled0.ipynb')


def test_save_notebook_with_nonempty_new_notebook_and_save(mocker, tabwidget):
    """Test that .save_notebook() on a newly created notebook saves the
    notebook, checks that it is empty, and if it is, asks to save it again,
    and if yes, does save it under a new name."""
    mock_question = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.QMessageBox.question',
        return_value=QMessageBox.Yes)
    client = tabwidget.create_new_client()
    client.save = mocker.Mock()
    tabwidget.wait_and_check_if_empty = mocker.Mock(return_value=False)
    tabwidget.save_as = mocker.Mock(return_value='newname.ipynb')

    result = tabwidget.save_notebook(client)

    client.save.assert_called()
    tabwidget.wait_and_check_if_empty.assert_called_once()
    mock_question.assert_called_once()
    tabwidget.save_as.assert_called_once()
    assert result == 'newname.ipynb'


def test_save_notebook_with_nonempty_new_notebook_and_no_save(
            mocker, tabwidget):
    """Test that .save_notebook() on a newly created notebook saves the
    notebook, checks that it is empty, and if it is, asks to save it again,
    and if no, does not save it under a new name."""
    mock_question = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.QMessageBox.question',
        return_value=QMessageBox.No)
    client = tabwidget.create_new_client()
    client.save = mocker.Mock()
    tabwidget.wait_and_check_if_empty = mocker.Mock(return_value=False)
    tabwidget.save_as = mocker.Mock(return_value='newname.ipynb')

    result = tabwidget.save_notebook(client)

    client.save.assert_called()
    tabwidget.wait_and_check_if_empty.assert_called_once()
    mock_question.assert_called_once()
    tabwidget.save_as.assert_not_called()
    assert result.endswith('untitled0.ipynb')


def test_wait_and_check_if_empty_when_empty(mocker, tabwidget):
    """Test that .wait_and_check_if_empty() returns True when called on a
    notebook that is empty."""
    contents = {'cells': []}
    mock_read = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.nbformat.read',
        return_value=contents)

    result = tabwidget.wait_and_check_if_empty('ham.ipynb')

    mock_read.assert_called_once()
    assert result is True


def test_wait_and_check_if_empty_when_not_empty(mocker, tabwidget):
    """Test that .wait_and_check_if_empty() returns False when called on a
    notebook that is not empty."""
    contents = {'cells': [{'source': 'not empty'}]}
    mock_read = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.nbformat.read',
        return_value=contents)

    result = tabwidget.wait_and_check_if_empty('ham.ipynb')

    mock_read.assert_called_once()
    assert result is False


@pytest.mark.parametrize('exception', [FileNotFoundError, NotJSONError])
def test_wait_and_check_if_empty_with_delay(mocker, tabwidget, exception):
    """Test that .wait_and_check_if_empty() on an empty notebook tries to read
    it, and when that fails because the file does not exist or is not JSON, it
    tries again to read it. When the read succeeds the second time and the
    notebook turns out to be empty, the function returns True."""
    contents = {'cells': []}
    mock_read = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.nbformat.read',
        side_effect=[exception, contents])

    result = tabwidget.wait_and_check_if_empty('ham.ipynb')

    assert mock_read.call_count == 2
    assert result is True


def test_wait_and_check_with_long_delay(mocker, tabwidget):
    """Test that .wait_and_check_if_empty() repeatedly tries to read the file,
    and when that keeps failing because the file does not exists, eventually
    gives up and returns True."""
    mock_read = mocker.patch(
        'spyder_notebook.widgets.notebooktabwidget.nbformat.read',
        side_effect=FileNotFoundError)

    result = tabwidget.wait_and_check_if_empty('ham.ipynb')

    assert mock_read.call_count == WAIT_SAVE_ITERATIONS
    assert result is True


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
