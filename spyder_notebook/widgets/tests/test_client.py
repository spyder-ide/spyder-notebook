# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License

"""Tests for client.py covering NotebookClient."""

# Third-party imports
import pytest
from qtpy.QtWidgets import QWidget

# Local imports
from spyder_notebook.widgets.client import NotebookClient


class MockPlugin(QWidget):
    def get_plugin_actions(self):
        return []


@pytest.fixture
def client(qtbot):
    """Construct a NotebookClient for use in tests."""
    plugin = MockPlugin()
    client = NotebookClient(plugin, '/path/notebooks/ham.ipynb')
    server_info = {'notebook_dir': '/path/notebooks',
                   'url': 'fake_url',
                   'token': 'fake_token'}
    client.register(server_info)
    return client


def test_notebookclient_get_kernel_id(client, mocker):
    """Basic unit test for NotebookClient.get_kernel_id()."""
    response = mocker.Mock()
    content = b'[{"kernel": {"id": "42"}, "notebook": {"path": "ham.ipynb"}}]'
    response.content = content
    mocker.patch('requests.get', return_value=response)

    kernel_id = client.get_kernel_id()
    assert kernel_id == '42'


def test_notebookclient_get_kernel_id_with_fields_missing(client, mocker):
    """Test NotebookClient.get_kernel_id() if response has fields missing."""
    response = mocker.Mock()
    content = (b'[{"kernel": {"id": "1"}, "notebook": {"spam": "eggs"}},'
               b' {"kernel": {"id": "2"}},'
               b' {"kernel": {"id": "3"}, "notebook": {"path": "ham.ipynb"}}]')
    response.content = content
    mocker.patch('requests.get', return_value=response)

    kernel_id = client.get_kernel_id()
    assert kernel_id == '3'
