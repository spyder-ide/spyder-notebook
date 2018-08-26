# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License

"""Tests for client.py covering NotebookClient."""

# Third-party imports
from qtpy.QtWidgets import QWidget

# Local imports
from spyder_notebook.widgets.client import NotebookClient


class MockPlugin(QWidget):
    def get_plugin_actions(self):
        return []


def test_notebookclient_get_kernel_id(qtbot, mocker):
    """Basic unit test for NotebookClient.get_kernel_id()."""
    plugin = MockPlugin()
    client = NotebookClient(plugin, '/path/notebooks/ham.ipynb')
    server_info = {'notebook_dir': '/path/notebooks',
                   'url': 'fake_url',
                   'token': 'fake_token'}
    client.register(server_info)
    response = mocker.Mock()
    response.content = (b'[{"kernel": {"id": "42"},'
                        b'  "notebook": {"path": "ham.ipynb"}}]')
    mocker.patch('requests.get', return_value=response)
    kernel_id = client.get_kernel_id()
    assert kernel_id == '42'
