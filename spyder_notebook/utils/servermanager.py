# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License

"""File implementing ServerManager."""

# Standard library imports
import datetime
import enum
import json
import logging
import os
import os.path as osp
import sys

# Qt imports
from qtpy.QtCore import QObject, QProcess, QProcessEnvironment, QTimer, Signal
from qtpy.QtWebEngineWidgets import QWebEngineProfile

# Third-party imports
from jupyter_core.paths import jupyter_runtime_dir
from jupyter_server import serverapp
from tornado.httpclient import HTTPClientError

# Spyder imports
from spyder.config.base import DEV, get_home_dir, get_module_path


# Kernel specification to use in notebook server
KERNELSPEC = 'spyder.plugins.ipythonconsole.utils.kernelspec.SpyderKernelSpec'

# Delay we wait to check whether server is up (in ms)
CHECK_SERVER_UP_DELAY = 250

# Delay before we give up on server starting (in s)
SERVER_TIMEOUT_DELAY = 30

logger = logging.getLogger(__name__)


class ServerState(enum.Enum):
    """State of a server process."""

    STARTING = 1
    RUNNING = 2
    FINISHED = 3
    ERROR = 4
    TIMED_OUT = 5


class ServerProcess:
    """
    Process executing a notebook server.

    This is a data class.
    """

    def __init__(self, process, notebook_dir, interpreter, info_file,
                 starttime=None, state=ServerState.STARTING, server_info=None,
                 output=''):
        """
        Construct a ServerProcess.

        Parameters
        ----------
        process : QProcess
            The process described by this instance.
        notebook_dir : str
            Directory from which the server can render notebooks.
        interpreter : str
            File name of Python interpreter used to render notebooks.
        info_file : str
            Name of JSON file in jupyter_runtime_dir() with connection
            information for the server.
        starttime : datetime or None, optional
            Time at which the process was started. The default is None,
            meaning that the current time should be used.
        state : ServerState, optional
            State of the server process. The default is ServerState.STARTING.
        server_info : dict or None, optional
            If set, this is a dict with the information in info_file. It has
            keys like 'url' and 'token'. The default is None.
        output : str
            Output of the server process from stdout and stderr. The default
            is ''.
        """
        self.process = process
        self.notebook_dir = notebook_dir
        self.interpreter = interpreter
        self.info_file = info_file
        self.starttime = starttime or datetime.datetime.now()
        self.state = state
        self.server_info = server_info
        self.output = output


class ServerManager(QObject):
    """
    Manager for notebook servers.

    A Jupyter notebook server will only render notebooks under a certain
    directory, so we may need several servers. This class manages all these
    servers.

    Attributes
    ----------
    dark_theme : bool
        Whether notebooks should be rendered using the dark theme.
    servers : list of ServerProcess
        List of servers managed by this object.
    """

    # A server has started and is now accepting requests
    sig_server_started = Signal(ServerProcess)

    # We tried to start a server but it took too long to start up
    sig_server_timed_out = Signal(ServerProcess)

    # We tried to start a server but an error occurred
    sig_server_errored = Signal(ServerProcess)

    def __init__(self, dark_theme=False):
        """
        Construct a ServerManager.

        This constructor also clears Qt WebEngine's HTTP cache, because for
        unknown reasons WebEngine seems to use out-of-date code after the
        JavaScript bundle is replaced.

        Parameters
        ----------
        dark_theme : bool, optional
            Whether notebooks should be rendered using the dark theme.
            The default is False.
        """
        super().__init__()
        self.dark_theme = dark_theme
        self.servers = []
        QWebEngineProfile.defaultProfile().clearHttpCache()

    def get_server(self, filename, interpreter, start=True):
        """
        Return server which can render a notebook or potentially start one.

        Return the server info of a server managed by this object which can
        render the notebook with the given file name and which uses the given
        interpreter. If no such server exists and `start` is True, then start
        up a server asynchronously (unless a suitable server is already in the
        process of starting up).

        Parameters
        ----------
        filename : str
            File name of notebook which is to be rendered.
        interpreter : str
            File name of Python interpreter to be used.
        start : bool, optional
            Whether to start up a server if none exists. The default is True.

        Returns
        -------
        dict or None
            A dictionary describing the server which can render the notebook,
            or None if no such server exists.
        """
        filename = osp.abspath(filename)
        for server in self.servers:
            if (filename.startswith(server.notebook_dir)
                    and interpreter == server.interpreter):
                if server.state == ServerState.RUNNING:
                    return server.server_info
                elif server.state == ServerState.STARTING:
                    logger.debug('Waiting for server for %s to start up',
                                 server.notebook_dir)
                    return None
        if start:
            self.start_server(filename, interpreter)
        return None

    def start_server(self, filename, interpreter):
        """
        Start a notebook server asynchronously.

        Start a server which can render the given notebook and return
        immediately. Assume the server uses the given interpreter. The manager
        will check periodically whether the server is accepting requests and
        emit `sig_server_started` or `sig_server_timed_out` when appropriate.

        Every server uses a unique file to store its connection number in.
        The name of this file is based on `self.servers`, under the assumption
        that entries are never removed from this list.

        Parameters
        ----------
        filename : str
            File name of notebook to be rendered by the server.
        interpreter : str
            File name of Python interpreter to be used.
        """
        home_dir = get_home_dir()
        if filename.startswith(home_dir):
            nbdir = home_dir
        else:
            nbdir = osp.dirname(filename)

        logger.debug('Starting new notebook server for %s', nbdir)
        process = QProcess(None)
        serverscript = osp.join(osp.dirname(__file__), '../server/main.py')
        serverscript = osp.normpath(serverscript)
        my_pid = os.getpid()
        server_index = len(self.servers) + 1
        info_file = f'spynbserver-{my_pid}-{server_index}.json'
        arguments = ['-m', 'spyder_notebook.server', '--no-browser',
                     f'--info-file={info_file}',
                     f'--notebook-dir={nbdir}',
                     '--ServerApp.password=',
                     f'--KernelSpecManager.kernel_spec_class={KERNELSPEC}']
        if self.dark_theme:
            arguments.append('--dark')

        logger.debug('Arguments: %s', repr(arguments))

        if DEV:
            env = QProcessEnvironment.systemEnvironment()
            env.insert('PYTHONPATH', osp.dirname(get_module_path('spyder')))
            process.setProcessEnvironment(env)

        server_process = ServerProcess(
            process, notebook_dir=nbdir, interpreter=interpreter,
            info_file=info_file)
        process.setProcessChannelMode(QProcess.MergedChannels)
        process.readyReadStandardOutput.connect(
            lambda: self.read_server_output(server_process))
        process.errorOccurred.connect(
            lambda error: self.handle_error(server_process, error))
        process.finished.connect(
            lambda code, status:
                self.handle_finished(server_process, code, status))

        process.start(sys.executable, arguments)
        self.servers.append(server_process)

        self._check_server_started(server_process)

    def _check_server_started(self, server_process):
        """
        Check whether a notebook server has started up.

        If the server state is no longer in the "starting" state (probably
        because an error occurred or the server exited prematurely) then
        do nothing.

        Otherwise, look for a json file in the Jupyter runtime dir to check
        whether the notebook server has started up. If so, then emit
        `sig_server_started` and fill the server info with the contents of the
        json file. If not, then schedule another check after a short delay
        (as set in CHECK_SERVER_UP_DELAY) unless the server is taken too long
        (as specified by SERVER_TIMEOUT_DELAY). In the latter case, emit
        sig_server_timed_out`.

        Parameters
        ----------
        server_process : ServerProcess
            The server process to be checked.
        """
        if server_process.state != ServerState.STARTING:
            return

        runtime_dir = jupyter_runtime_dir()
        filename = osp.join(runtime_dir, server_process.info_file)

        try:
            with open(filename, encoding='utf-8') as f:
                server_info = json.load(f)
        except (OSError, json.JSONDecodeError):
            # E.g., file does not (yet) exist or is still being written
            logger.debug(f'Error when opening {filename}')
            delay = datetime.datetime.now() - server_process.starttime
            if delay > datetime.timedelta(seconds=SERVER_TIMEOUT_DELAY):
                logger.debug('Notebook server for %s timed out',
                             server_process.notebook_dir)
                server_process.state = ServerState.TIMED_OUT
                self.sig_server_timed_out.emit(server_process)
            else:
                QTimer.singleShot(
                    CHECK_SERVER_UP_DELAY,
                    lambda: self._check_server_started(server_process))
            return None

        logger.debug('Server for %s started', server_process.notebook_dir)
        server_process.state = ServerState.RUNNING
        server_process.server_info = server_info
        self.sig_server_started.emit(server_process)

    def shutdown_all_servers(self):
        """
        Shutdown all servers.

        Disconnect all signals of the server process and try to shutdown the
        server nicely. However, if the server is still starting up, or if
        shutting down nicely does not work, then kill the server process.
        """
        for server in self.servers:
            process = server.process
            process.readyReadStandardOutput.disconnect()
            process.errorOccurred.disconnect()
            process.finished.disconnect()

            if server.state == ServerState.RUNNING:
                logger.debug('Shutting down notebook server for %s',
                             server.notebook_dir)

                try:
                    serverapp.shutdown_server(server.server_info, log=logger)
                except HTTPClientError as err:
                    # No response received, typically due to time out
                    if err.code == 599:
                        logger.warning('Ignoring HTTPClientError '
                                       'with code = 599')
                    else:
                        raise
                except ConnectionError as err:
                    logger.warning(f'Ignoring {err}')
                server.state = ServerState.FINISHED

            if server.state == ServerState.STARTING:
                process.kill()
                server.state = ServerState.FINISHED

            if process.state() != QProcess.NotRunning:
                # Should not be necessary, but make sure that process is killed
                process.kill()


    def read_server_output(self, server_process):
        """
        Read the output of the notebook server process.

        This function is connected to the QProcess.readyReadStandardOutput
        signal. It reads the contents of the standard output channel of the
        server process and stores it in `server_process.output`. The standard
        error channel is merged into the standard output channel.

        Parameters
        ----------
        server_process : ServerProcess
            The server process whose output is to be read.
        """
        byte_array = server_process.process.readAllStandardOutput()
        output = byte_array.data().decode(errors='backslashreplace')
        server_process.output += output

    def handle_error(self, server_process, error):
        """
        Handle errors that occurred in the notebook server process.

        This function is connected to the QProcess.errorOccurred signal.
        It changes the state of the process and emits `sig_server_errored`.

        Parameters
        ----------
        server_process : ServerProcess
            The server process that encountered an error
        error : QProcess.ProcessError
            Error as determined by Qt.
        """
        logger.debug('Server for %s encountered error %s',
                     server_process.notebook_dir, str(error))
        server_process.state = ServerState.ERROR
        self.sig_server_errored.emit(server_process)

    def handle_finished(self, server_process, code, status):
        """
        Handle signal that notebook server process has finished.

        This function is connected to the QProcess.finished signal.
        It changes the state of the process.

        Parameters
        ----------
        server_process : ServerProcess
            The server process that encountered an error.
        code : int
            Exit code as reported by Qt.
        status : QProcess.ExitStatus
            Exit status as reported by Qt.
        """
        logger.debug('Server for %s finished with code = %d, status = %s',
                     server_process.notebook_dir, code, str(status))
        server_process.state = ServerState.FINISHED
