# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for servermanager.py"""

# Standard library imports
import datetime
import os.path as osp

# Third party imports
import pytest

# Qt imports
from qtpy.QtCore import QByteArray, QProcess, QTimer

# Local imports
from spyder_notebook.utils.servermanager import (
    ServerManager, ServerProcess, ServerState)


@pytest.mark.parametrize('start_arg', [True, False])
def test_get_server_without_servers(mocker, start_arg):
    """Test that .get_server() calls .start_server() when there are no servers
    only if `start` is True."""
    serverManager = ServerManager()
    mock_start = mocker.patch.object(serverManager, 'start_server')
    filename = osp.abspath('ham.ipynb')
    interpreter = '/ham/imterpreter'

    res = serverManager.get_server(filename, interpreter, start=start_arg)

    assert res is None
    if start_arg:
        mock_start.assert_called_once_with(filename, interpreter)
    else:
        mock_start.assert_not_called()


@pytest.mark.parametrize(
    ('nbdir', 'interpreter', 'state',              'result', 'start'),
    [('foo',  'ham',         ServerState.RUNNING,   True,     False),
     ('',     'ham',         ServerState.RUNNING,   True,     False),
     ('foo',  'ham',         ServerState.STARTING,  False,    False),
     ('foo',  'ham',         ServerState.TIMED_OUT, False,    True),
     ('bar',  'ham',         ServerState.RUNNING,   False,    True),
     ('foo',  'cheese',      ServerState.RUNNING,   False,    True)])
def test_get_server_with_server(
        mocker, nbdir, interpreter, state, result, start):
    """Test that .get_server() returns a suitable server if it is accepting
    requests, and that it start up a new server unless a suitable server exists
    that is either starting up or running. Here, a suitable server is a server
    which renders the given notebook with the correct interpreter."""
    serverManager = ServerManager()
    mock_start = mocker.patch.object(serverManager, 'start_server')
    filename = osp.abspath('foo/ham.ipynb')
    server_info = mocker.Mock(spec=dict)
    server = ServerProcess(
        mocker.Mock(spec=QProcess), osp.abspath(nbdir), interpreter,
        'info.json', state=state, server_info=server_info)
    serverManager.servers.append(server)

    res = serverManager.get_server(filename, interpreter='ham')

    if result:
        assert res == server_info
    else:
        assert res is None
    if start:
        mock_start.assert_called_once_with(filename, 'ham')
    else:
        mock_start.assert_not_called()


@pytest.mark.parametrize(('dark', 'under_home'),
                         [(True, True), (False, True), (False, False)])
def test_start_server(mocker, dark, under_home):
    """
    Test that .start_server() starts a process with the correct arguments,
    that it stores the server process in `.servers`; and that it calls
    ._check_server_running().
    """
    serverManager = ServerManager(dark)
    mock_check = mocker.patch.object(serverManager, '_check_server_started')
    mock_QProcess = mocker.patch(
        'spyder_notebook.utils.servermanager.QProcess', spec=QProcess)
    mocker.patch(
        'spyder_notebook.utils.servermanager.get_home_dir', return_value='foo')
    if under_home:
        filename = osp.join('foo', 'bar', 'ham.ipynb')
        nbdir = osp.join('foo')
    else:
        filename = osp.join('notfoo', 'bar', 'ham.ipynb')
        nbdir = osp.join('notfoo', 'bar')

    serverManager.start_server(filename, '/ham/interpreter')

    mock_QProcess.return_value.start.assert_called_once()
    args = mock_QProcess.return_value.start.call_args[0]
    assert '--notebook-dir={}'.format(nbdir) in args[1]
    assert ('--dark' in args[1]) == dark
    assert len(serverManager.servers) == 1
    assert serverManager.servers[0].process == mock_QProcess.return_value
    assert serverManager.servers[0].notebook_dir == nbdir
    mock_check.assert_called_once()


def test_check_server_started_if_started(mocker, qtbot):
    """Test that .check_server_started() emits sig_server_started if there
    is a json file with the correct name and completes the server info."""
    fake_open = mocker.patch('spyder_notebook.utils.servermanager.open',
                             mocker.mock_open(read_data='{"foo": 42}'))
    mocker.patch('spyder_notebook.utils.servermanager.jupyter_runtime_dir',
                 return_value='runtimedir')
    mock_process = mocker.Mock(spec=QProcess)
    server_process = ServerProcess(
        mock_process, 'notebookdir', 'interpreter', 'info.json')
    serverManager = ServerManager()

    with qtbot.waitSignal(serverManager.sig_server_started):
        serverManager._check_server_started(server_process)

    fake_open.assert_called_once_with(
        osp.join('runtimedir', 'info.json'), encoding='utf-8')
    assert server_process.state == ServerState.RUNNING
    assert server_process.server_info == {'foo': 42}


def test_check_server_started_if_not_started(mocker, qtbot):
    """Test that .check_server_started() repeats itself on a timer if there
    is no json file with the correct name."""
    fake_open = mocker.patch('spyder_notebook.utils.servermanager.open',
                             side_effect=OSError)
    mocker.patch('spyder_notebook.utils.servermanager.jupyter_runtime_dir',
                 return_value='runtimedir')
    mock_QTimer = mocker.patch('spyder_notebook.utils.servermanager.QTimer',
                               spec=QTimer)
    mock_process = mocker.Mock(spec=QProcess)
    server_process = ServerProcess(
        mock_process, 'notebookdir', 'interpreter', 'info.json')
    serverManager = ServerManager()

    serverManager._check_server_started(server_process)

    fake_open.assert_called_once_with(
        osp.join('runtimedir', 'info.json'), encoding='utf-8')
    assert server_process.state == ServerState.STARTING
    mock_QTimer.singleShot.assert_called_once()


def test_check_server_started_if_timed_out(mocker, qtbot):
    """Test that .check_server_started() emits sig_server_timed_out if after
    an hour there is still no json file."""
    fake_open = mocker.patch('spyder_notebook.utils.servermanager.open',
                             side_effect=OSError)
    mocker.patch('spyder_notebook.utils.servermanager.jupyter_runtime_dir',
                 return_value='runtimedir')
    mock_process = mocker.Mock(spec=QProcess)
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    server_process = ServerProcess(
        mock_process, 'notebookdir', 'interpreter', 'info.json',
        starttime=one_hour_ago)
    serverManager = ServerManager()

    with qtbot.waitSignal(serverManager.sig_server_timed_out):
        serverManager._check_server_started(server_process)

    fake_open.assert_called_once_with(
        osp.join('runtimedir', 'info.json'), encoding='utf-8')
    assert server_process.state == ServerState.TIMED_OUT


def test_check_server_started_if_errored(mocker, qtbot):
    """Test that .check_server_started() does not do anything if server state
    is ERROR."""
    fake_open = mocker.patch('spyder_notebook.utils.servermanager.open')
    mock_QTimer = mocker.patch('spyder_notebook.utils.servermanager.QTimer',
                               spec=QTimer)
    mock_process = mocker.Mock(spec=QProcess)
    server_process = ServerProcess(
        mock_process, 'notebookdir', 'interpreter', 'info.json',
        state=ServerState.ERROR)
    serverManager = ServerManager()

    serverManager._check_server_started(server_process)

    fake_open.assert_not_called()
    mock_QTimer.assert_not_called()
    assert server_process.state == ServerState.ERROR


def test_shutdown_all_servers(mocker):
    """Test that .shutdown_all_servers() does shutdown all running servers,
    but not servers in another state."""
    mock_shutdown = mocker.patch(
        'spyder_notebook.utils.servermanager.serverapp.shutdown_server')
    server1 = ServerProcess(
        mocker.Mock(spec=QProcess), '', '', '', state=ServerState.RUNNING,
        server_info=mocker.Mock(dict))
    server2 = ServerProcess(
        mocker.Mock(spec=QProcess), '', '', '', state=ServerState.ERROR,
        server_info=mocker.Mock(dict))
    serverManager = ServerManager()
    serverManager.servers = [server1, server2]

    serverManager.shutdown_all_servers()

    assert mock_shutdown.called_once_with(server1.server_info)
    assert server1.state == ServerState.FINISHED
    assert server2.state == ServerState.ERROR


def test_read_standard_output(mocker):
    """Test that .read_standard_output() stores the output."""
    before = 'before\n'
    output = 'Αθήνα\n'  # check that we can handle non-ascii
    mock_read = mocker.Mock(return_value=QByteArray(output.encode()))
    mock_process = mocker.Mock(spec=QProcess, readAllStandardOutput=mock_read)
    server = ServerProcess(mock_process, '', '', '', output=before)
    serverManager = ServerManager()
    serverManager.servers = [server]

    serverManager.read_server_output(server)

    mock_read.assert_called_once()
    assert server.output == before + output


def test_handle_error(mocker, qtbot):
    """Test that .handle_error() changes the state and emits signal."""
    server = ServerProcess(mocker.Mock(spec=QProcess), '', '', '')
    serverManager = ServerManager()

    with qtbot.waitSignal(serverManager.sig_server_errored):
        serverManager.handle_error(server, mocker.Mock())

    assert server.state == ServerState.ERROR


def test_handle_finished(mocker, qtbot):
    """Test that .handle_finished() changes the state."""
    server = ServerProcess(mocker.Mock(spec=QProcess), '', '', '')
    serverManager = ServerManager()

    serverManager.handle_finished(server, 42, mocker.Mock())

    assert server.state == ServerState.FINISHED
