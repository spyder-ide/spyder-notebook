# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""File implementing NotebookTabWidget."""

# Standard library imports
import logging
import os
import os.path as osp
import sys

# Qt imports
from qtpy.compat import getopenfilenames, getsavefilename
from qtpy.QtCore import QEventLoop, QTimer
from qtpy.QtWidgets import QMessageBox

# Third-party imports
import nbformat

# Spyder imports
from spyder.config.manager import CONF
from spyder.utils.misc import get_python_executable
from spyder.utils.programs import get_temp_dir, is_python_interpreter
from spyder.widgets.tabs import Tabs

# Local imports
from spyder_notebook.utils.localization import _
from spyder_notebook.widgets.client import NotebookClient


# Directory in which new notebooks are created
NOTEBOOK_TMPDIR = osp.join(get_temp_dir(), 'notebooks')

# Path to HTML file with welcome message
PACKAGE_PATH = osp.join(osp.dirname(__file__), '..')
WELCOME = osp.join(PACKAGE_PATH, 'utils', 'templates', 'welcome.html')
WELCOME_DARK = osp.join(PACKAGE_PATH, 'utils', 'templates',
                        'welcome-dark.html')

# Filter to use in file dialogs
FILES_FILTER = '{} (*.ipynb)'.format(_('Jupyter notebooks'))

# How long to wait after save before checking whether file exists (in ms)
WAIT_SAVE_DELAY = 250

# How often to wait for that time
WAIT_SAVE_ITERATIONS = 20

logger = logging.getLogger(__name__)


class NotebookTabWidget(Tabs):
    """
    Tabbed widget whose tabs display notebooks.

    This is the main widget of the notebook plugin.

    Attributes
    ----------
    actions : list of (QAction or QMenu or None) or None
        Items to be added to the context menu.
    dark_theme : bool
        Whether to display notebooks in a dark theme. The default is False.
    untitled_num : int
        Number used in file name of newly created notebooks.
    """

    def __init__(self, parent, server_manager, actions=None, menu=None,
                 corner_widgets=None, dark_theme=False):
        """
        Construct a NotebookTabWidget.

        Parameters
        ----------
        parent : QWidget
            Parent of the tabbed widget.
        actions : list of (QAction or QMenu or None) or None
            Items to be added to the context menu.
        menu : QMenu or None
            Context menu of the tabbed widget.
        corner_widgets : dict of (Qt.Corner, list of QWidget or int) or None
            Widgets to be placed in the top left and right corner of the
            tabbed widget. A button for browsing the tabs is always added to
            the top left corner.
        """
        super().__init__(parent, actions, menu, corner_widgets)

        self.actions = actions
        self.dark_theme = dark_theme
        self.untitled_num = 0

        self.server_manager = server_manager
        self.server_manager.sig_server_started.connect(
            self.handle_server_started)
        self.server_manager.sig_server_timed_out.connect(
            self.handle_server_timed_out_or_error)
        self.server_manager.sig_server_errored.connect(
            self.handle_server_timed_out_or_error)

        if not sys.platform == 'darwin':
            # Don't set document mode to true on OSX because it generates
            # a crash when the console is detached from the main window
            # Fixes spyder-ide/spyder#561
            self.setDocumentMode(True)

        self.set_close_function(self.close_client)

    def open_notebook(self, filenames=None):
        """
        Open a notebook from file.

        Parameters
        ----------
        filenames : list of str or None, optional
            List of file names of notebooks to open. The default is None,
            meaning that the user should be asked.

        Returns
        -------
        filenames : list of str
            List of file names of notebooks that were opened.
        """
        if not filenames:
            filenames, _selfilter = getopenfilenames(
                self, _('Open notebook'), '', FILES_FILTER)
        if filenames:
            for filename in filenames:
                self.create_new_client(filename=filename)
        return filenames

    def create_new_client(self, filename=None):
        """
        Create a new notebook or load a pre-existing one.

        Parameters
        ----------
        filename : str, optional
            File name of the notebook to load in the new client. The default
            is None, meaning that a new notebook should be created.

        Returns
        -------
        client : NotebookClient or None
            Notebook client that is opened, or None if unsuccessful.
        """
        # Generate the notebook name (in case of a new one)
        if not filename:
            if not osp.isdir(NOTEBOOK_TMPDIR):
                os.makedirs(NOTEBOOK_TMPDIR)
            nb_name = 'untitled' + str(self.untitled_num) + '.ipynb'
            filename = osp.join(NOTEBOOK_TMPDIR, nb_name)
            kernelspec = dict(display_name='Python 3 (Spyder)',
                              name='python3')
            metadata = dict(kernelspec=kernelspec)
            nb_contents = nbformat.v4.new_notebook(metadata=metadata)
            nbformat.write(nb_contents, filename)
            self.untitled_num += 1

        client = NotebookClient(self, filename, self.actions)
        self.add_tab(client)
        interpreter = self.get_interpreter()
        server_info = self.server_manager.get_server(
            filename, interpreter, start=True)
        if server_info:
            logger.debug('Using existing server at %s',
                         server_info['notebook_dir'])
            client.register(server_info)
            client.load_notebook()
        return client

    @staticmethod
    def get_interpreter():
        """
        Return the Python interpreter to be used in notebooks.

        This function looks in the Spyder configuration to determine and
        return the Python interpreter to be used in notebooks, which is the
        same as is used in consoles.

        Returns
        -------
        The file name of the interpreter
        """
        if CONF.get('main_interpreter', 'default'):
            pyexec = get_python_executable()
        else:
            pyexec = CONF.get('main_interpreter', 'executable')
            if not is_python_interpreter(pyexec):
                pyexec = get_python_executable()
        return pyexec

    def maybe_create_welcome_client(self):
        """
        Create a welcome tab if there are no tabs.

        Returns
        -------
        client : NotebookClient or None
            The client in the created tab, or None if no tab is created.
        """
        if self.count() == 0:
            if self.dark_theme:
                welcome = open(WELCOME_DARK).read()
            else:
                welcome = open(WELCOME).read()
            client = NotebookClient(
                self, WELCOME, self.actions, ini_message=welcome)
            self.add_tab(client)
            return client

    def close_client(self, index=None, save_before_close=True):
        """
        Close client tab with given index (or close current tab).

        First save the notebook (unless this is the welcome client or
        `save_before_close` is False). Then delete the notebook if it is in
        `get_temp_dir()`. Then shutdown the kernel of the notebook and close
        the tab. Finally, create a welcome tab if there are no tabs.

        Parameters
        ----------
        index : int or None, optional
            Index of tab to be closed. The default is None, meaning that the
            current tab is closed.
        save_before_close : bool, optional
            Whether to save the notebook before closing the tab. The default
            is True.

        Returns
        -------
        The file name of the notebook, or None if no tab was closed.
        """
        if not self.count():
            return None
        if index is None:
            index = self.currentIndex()
        client = self.widget(index)

        filename = client.filename
        if not self.is_welcome_client(client):
            if save_before_close:
                filename = self.save_notebook(client)
            client.shutdown_kernel()
        client.close()

        # Delete notebook file if it is in temporary directory
        if filename.startswith(get_temp_dir()):
            try:
                os.remove(filename)
            except EnvironmentError:
                pass

        # Note: notebook index may have changed after closing related widgets
        self.removeTab(self.indexOf(client))
        self.maybe_create_welcome_client()
        return filename

    def save_notebook(self, client):
        """
        Save notebook corresponding to given client.

        If the notebook is newly created and not empty, then ask the user
        whether to save it under a new name.

        Parameters
        ----------
        client : NotebookClient
            Client of notebook to be saved.

        Returns
        -------
        The file name of the notebook.
        """
        client.save()
        filename = client.filename
        if not self.is_newly_created(client):
            return filename
        if self.wait_and_check_if_empty(filename):
            return filename

        # Notebook not empty, so ask user to save with new filename
        buttons = QMessageBox.Yes | QMessageBox.No
        text = _("<b>{0}</b> has been modified.<br>"
                 "Do you want to save changes?").format(osp.basename(filename))
        answer = QMessageBox.question(
            self, _('Save changes'), text, buttons)
        if answer == QMessageBox.Yes:
            return self.save_as(reopen_after_save=False)
        else:
            return filename

    @staticmethod
    def wait_and_check_if_empty(filename):
        """
        Wait until notebook is created and check whether it is empty.

        Repeatedly try to read the file, waiting a bit after every attempt.
        At the first attempt where the file exists, test whether it is empty
        and return. If it takes too long before the file is created, pretend
        it is empty.

        Parameters
        ----------
        filename : str
            File name of notebook to be checked.

        Returns
        -------
        True if notebook is empty or on timeout, False otherwise.
        """
        for iteration in range(WAIT_SAVE_ITERATIONS):

            # Wait a bit
            wait_save = QEventLoop()
            QTimer.singleShot(WAIT_SAVE_DELAY, wait_save.quit)
            wait_save.exec_()

            # Try reading the file
            try:
                nb_contents = nbformat.read(filename, as_version=4)
            except FileNotFoundError:
                continue

            # If empty, we are done
            if (len(nb_contents['cells']) == 0
                    or len(nb_contents['cells'][0]['source']) == 0):
                return True
            else:
                return False
        else:
            # It is taking longer than expected;
            # Just return True and hope for the best
            return True

    def save_as(self, name=None, reopen_after_save=True):
        """
        Save current notebook under a different file name.

        First, save the notebook under the original file name. Then ask user
        for a new file name (if `name` is not set), and return if no new name
        is given. Then, read the contents of the notebook that was just saved
        and write them under the new file name. If `reopen_after_save` is
        True, then close the original tab and open a new tab with the
        notebook loaded from the new file name.

        Parameters
        ----------
        name : str or None, optional
            File name under which the notebook is to be saved. The default is
            None, meaning that the user should be asked for the file name.
        reopen_after_save : bool, optional
            Whether to close the original tab and re-open it under the new
            file name after saving the notebook. The default is True.

        Returns
        -------
        The file name of the notebook.
        """
        current_client = self.currentWidget()
        current_client.save()
        original_path = current_client.get_filename()
        if not name:
            original_name = osp.basename(original_path)
        else:
            original_name = name
        filename, _selfilter = getsavefilename(self, _("Save notebook"),
                                               original_name, FILES_FILTER)
        if not filename:
            return original_path

        try:
            nb_contents = nbformat.read(original_path, as_version=4)
        except EnvironmentError as error:
            txt = (_("Error while reading {}<p>{}")
                   .format(original_path, str(error)))
            QMessageBox.critical(self, _("File Error"), txt)
            return original_path
        try:
            nbformat.write(nb_contents, filename)
        except EnvironmentError as error:
            txt = (_("Error while writing {}<p>{}")
                   .format(filename, str(error)))
            QMessageBox.critical(self, _("File Error"), txt)
            return original_path
        if reopen_after_save:
            self.close_client(save_before_close=False)
            self.create_new_client(filename=filename)
        return filename

    @staticmethod
    def is_newly_created(client):
        """
        Return whether client has a newly created notebook.

        This only looks at the file name of the notebook. If it has the form
        of file names of newly created notebooks, the function returns True.

        Parameters
        ----------
        client : NotebookClient
            Client under consideration.

        Returns
        -------
        True if notebook is newly created, False otherwise.
        """
        path = client.get_filename()
        dirname, basename = osp.split(path)
        return dirname == NOTEBOOK_TMPDIR and basename.startswith('untitled')

    @staticmethod
    def is_welcome_client(client):
        """
        Return whether some client is a newly created notebook.

        Parameters
        ----------
        client : NotebookClient
            Client under consideration.

        Returns
        -------
        True if `client` is a welcome client, False otherwise.
        """
        return client.get_filename() in [WELCOME, WELCOME_DARK]

    def add_tab(self, widget):
        """
        Add tab containing some notebook widget to the tabbed widget.

        Parameters
        ----------
        widget : NotebookClient
            Notebook widget to display in new tab.
        """
        index = self.addTab(widget, widget.get_short_name())
        self.setCurrentIndex(index)
        self.setTabToolTip(index, widget.get_filename())

    def handle_server_started(self, process):
        """
        Handle signal that a notebook server has started.

        Go through all notebook tabs which do not have server info and try
        getting the server info for them. If that marches the server process
        that has started, then update the notebook tab.

        Parameters
        ----------
        process : ServerProcess
            Info about the server that has started.
        """
        pid = process.process.processId()
        for client_index in range(self.count()):
            client = self.widget(client_index)
            if not client.static and not client.server_url:
                logger.debug('Getting server for %s', client.filename)
                server_info = self.server_manager.get_server(
                    client.filename, process.interpreter, start=False)
                if server_info and server_info['pid'] == pid:
                    logger.debug('Success')
                    client.register(server_info)
                    client.load_notebook()

    def handle_server_timed_out_or_error(self, process):
        """
        Display message box that server failed to start.

        Parameters
        ----------
        process : ServerProcess
            Info about the server that failed to start.
        """
        QMessageBox.critical(
            self,
            _("Server error"),
            _("The Spyder Notebook server failed to start or it is "
              "taking too much time to do it. Please select 'Server info' "
              "in the plugin's option menu to check for errors."))
        # Create a welcome widget, see gh:spyder-ide/spyder-notebook#93
        self.untitled_num -= 1
        self.maybe_create_welcome_client()
        return None
