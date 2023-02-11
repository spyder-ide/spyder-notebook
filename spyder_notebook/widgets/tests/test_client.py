# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License

"""Tests for client.py covering NotebookClient."""

# Third-party imports
import pytest
from qtpy.QtCore import QUrl
from qtpy.QtWidgets import QWidget
import requests

# Local imports
from spyder_notebook.widgets.client import NotebookClient


class MockPlugin(QWidget):
    def get_plugin_actions(self):
        return []


@pytest.fixture
def plugin_without_server(qtbot):
    """
    Construct mock plugin with NotebookClient but no notebook server.

    Use `plugin.client` to access the client.
    """
    plugin = MockPlugin()
    qtbot.addWidget(plugin)
    client = NotebookClient(plugin, '/path/notebooks/ham.ipynb')
    plugin.client = client
    return plugin


@pytest.fixture
def plugin(plugin_without_server):
    """
    Construct mock plugin with NotebookClient with server registered.

    Use `plugin.client` to access the client.
    """
    server_info = {'notebook_dir': '/path/notebooks',
                   'url': 'fake_url',
                   'token': 'fake_token'}
    plugin_without_server.client.register(server_info)
    return plugin_without_server


@pytest.mark.skip
def test_notebookwidget_create_window(plugin, mocker, qtbot):
    """Test that NotebookWidget.create_window() creates an object that calls
    webbrowser.open() when its URL is set."""
    widget = plugin.client.notebookwidget
    mock_notebook_open = mocker.patch('webbrowser.open')
    new_view = widget.createWindow(42)
    url = 'https://www.spyder-ide.org/'

    with qtbot.waitSignal(new_view.loadFinished):
        new_view.setUrl(QUrl(url))

    mock_notebook_open.assert_called_once_with(url)


def test_notebookclient_get_kernel_id(plugin, mocker):
    """Basic unit test for NotebookClient.get_kernel_id()."""
    response = mocker.Mock()
    content = b'[{"kernel": {"id": "42"}, "notebook": {"path": "ham.ipynb"}}]'
    response.content = content
    response.status_code = requests.codes.ok
    mocker.patch('requests.get', return_value=response)

    kernel_id = plugin.client.get_kernel_id()
    assert kernel_id == '42'


def test_notebookclient_get_kernel_id_without_server(
        plugin_without_server, mocker):
    """Test NotebookClient.get_kernel_id() if client has no server."""
    mock_get = mocker.patch('requests.get')

    kernel_id = plugin_without_server.client.get_kernel_id()

    assert kernel_id is None
    mock_get.assert_not_called()


def test_notebookclient_get_kernel_id_with_fields_missing(plugin, mocker):
    """Test NotebookClient.get_kernel_id() if response has fields missing."""
    response = mocker.Mock()
    content = (b'[{"kernel": {"id": "1"}, "notebook": {"spam": "eggs"}},'
               b' {"kernel": {"id": "2"}},'
               b' {"kernel": {"id": "3"}, "notebook": {"path": "ham.ipynb"}}]')
    response.content = content
    response.status_code = requests.codes.ok
    mocker.patch('requests.get', return_value=response)

    kernel_id = plugin.client.get_kernel_id()
    assert kernel_id == '3'


def test_notebookclient_get_kernel_id_with_error_status(plugin, mocker):
    """Test NotebookClient.get_kernel_id() when response has error status.
    In this case, the content of the response may be empty;
    see spyder-ide/spyder-notebook#317."""
    response = mocker.Mock()
    content = b''
    response.content = content
    response.status_code = requests.codes.forbidden
    mocker.patch('requests.get', return_value=response)
    MockMessageBox = mocker.patch('spyder_notebook.widgets.client.QMessageBox')

    plugin.client.get_kernel_id()

    MockMessageBox.warning.assert_called()


def test_notebookclient_get_kernel_id_with_exception(plugin, mocker):
    """Test NotebookClient.get_kernel_id() when request raises an exception."""
    exception = requests.exceptions.ProxyError('kaboom')
    mocker.patch('requests.get', side_effect=exception)
    MockMessageBox = mocker.patch('spyder_notebook.widgets.client.QMessageBox')

    plugin.client.get_kernel_id()

    MockMessageBox.warning.assert_called()
