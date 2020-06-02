# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for nbopen.py"""

# Local imports
from spyder_notebook.utils.nbopen import nbopen


def test_nbopen_with_no_running_servers(mocker, tmpdir):
    """Test that if nbopen is called when no servers are running, this calls
    Popen (to start the server) and atexit.register to register the shutdown
    function."""
    filename = str(tmpdir + 'ham.ipynb')
    serverinfo = {'notebook_dir': str(tmpdir)}
    mock_lrs = mocker.Mock(side_effect=[[], [serverinfo]])
    mock_shutdown = mocker.Mock()
    mocker.patch(
        'spyder_notebook.utils.nbopen.notebookapp',
        list_running_servers=mock_lrs,
        shutdown_server=mock_shutdown)
    mock_Popen = mocker.patch('spyder_notebook.utils.nbopen.subprocess.Popen')
    mock_register = mocker.patch(
        'spyder_notebook.utils.nbopen.atexit.register')

    res = nbopen(filename)

    assert res == serverinfo
    mock_Popen.assert_called_once()
    mock_register.assert_called_once()
    args, kwargs = mock_register.call_args
    assert args == (mock_shutdown, serverinfo)
