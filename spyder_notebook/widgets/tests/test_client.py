# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License

"""Tests for client.py covering NotebookClient."""

# Third-party imports
import pytest
from qtpy.QtWidgets import QWidget
import requests

# Local imports
from spyder_notebook.widgets.client import NotebookClient


class MockPlugin(QWidget):
    def get_plugin_actions(self):
        return []

@pytest.fixture
def plugin(qtbot):
    """
    Construct mock plugin with NotebookClient for use in tests.

    Use `plugin.client` to access the client.
    """
    plugin = MockPlugin()
    qtbot.addWidget(plugin)
    client = NotebookClient(plugin, '/path/notebooks/ham.ipynb')
    plugin.client = client
    server_info = {'notebook_dir': '/path/notebooks',
                   'url': 'fake_url',
                   'token': 'fake_token'}
    client.register(server_info)
    return plugin


def test_notebookclient_get_kernel_id(plugin, mocker):
    """Basic unit test for NotebookClient.get_kernel_id()."""
    response = mocker.Mock()
    content = b'[{"kernel": {"id": "42"}, "notebook": {"path": "ham.ipynb"}}]'
    response.content = content
    response.status_code = requests.codes.ok
    mocker.patch('requests.get', return_value=response)

    kernel_id = plugin.client.get_kernel_id()
    assert kernel_id == '42'


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
    """Test NotebookClient.get_kernel_id() when response has error status."""
    response = mocker.Mock()
    content = b'{"message": "error"}'
    response.content = content
    response.status_code = requests.codes.forbidden
    mocker.patch('requests.get', return_value=response)
    MockMessageBox = mocker.patch('spyder_notebook.widgets.client.QMessageBox')

    plugin.client.get_kernel_id()

    MockMessageBox.warning.assert_called()
