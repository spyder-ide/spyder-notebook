# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""File implementing NotebookTabWidget."""

# Standard library imports
import os
import os.path as osp
import subprocess
import sys

# Qt imports
from qtpy.compat import getopenfilenames
from qtpy.QtWidgets import QMessageBox

# Third-party imports
import nbformat

# Spyder imports
from spyder.config.base import _
from spyder.utils.programs import get_temp_dir
from spyder.widgets.tabs import Tabs

# Local imports
from spyder_notebook.utils.nbopen import nbopen, NBServerError
from spyder_notebook.widgets.client import NotebookClient


# Directory in which new notebooks are created
NOTEBOOK_TMPDIR = osp.join(get_temp_dir(), 'notebooks')

# Path to HTML file with welcome message
PACKAGE_PATH = osp.join(osp.dirname(__file__), '..')
WELCOME = osp.join(PACKAGE_PATH, 'utils', 'templates', 'welcome.html')

# Filter to use in file dialogs
FILES_FILTER = '{} (*.ipynb)'.format(_('Jupyter notebooks'))


class NotebookTabWidget(Tabs):
    """
    Tabbed widget whose tabs display notebooks.

    This is the main widget of the notebook plugin.

    Attributes
    ----------
    actions : list of (QAction or QMenu or None) or None
        Items to be added to the context menu.
    clients : list of NotebookClient
        List of notebook clients displayed in tabs in this widget.
    untitled_num : int
        Number used in file name of newly created notebooks.
    """

    def __init__(self, parent, actions, menu, corner_widgets):
        """
        Constructor.

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
        self.clients = []
        self.untitled_num = 0

        if not sys.platform == 'darwin':
            # Don't set document mode to true on OSX because it generates
            # a crash when the console is detached from the main window
            # Fixes spyder-ide/spyder#561
            self.setDocumentMode(True)

    def open_notebook(self, filenames=None):
        """
        Open a notebook from file.

        Parameters
        ----------
        filenames : list of str or None, optional
            List of file names of notebooks to open. The default is None,
            meaning that the user should be asked.
        """
        if not filenames:
            filenames, _selfilter = getopenfilenames(
                self, _('Open notebook'), '', FILES_FILTER)
        if filenames:
            for filename in filenames:
                self.create_new_client(filename=filename)

    def create_new_client(self, filename=None):
        """
        Create a new notebook or load a pre-existing one.

        This function also creates and selects a welcome tab, if no tabs are
        present.

        Parameters
        ----------
        filename : str, optional
            File name of the notebook to load in the new client. The default
            is None, meaning that a new notebook should be created.

        Returns
        -------
        filename : str or None
            File name of notebook that is opened, or None if unsuccessful.
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

        # Open the notebook with nbopen and get the url we need to render
        try:
            server_info = nbopen(filename)
        except (subprocess.CalledProcessError, NBServerError):
            QMessageBox.critical(
                self,
                _("Server error"),
                _("The Jupyter Notebook server failed to start or it is "
                  "taking too much time to do it. Please start it in a "
                  "system terminal with the command 'jupyter notebook' to "
                  "check for errors."))
            # Create a welcome widget
            # See issue 93
            self.untitled_num -= 1
            self.maybe_create_welcome_client()
            return

        welcome_client = self.maybe_create_welcome_client()
        client = NotebookClient(self, filename, self.actions)
        self.add_tab(client)
        client.register(server_info)
        client.load_notebook()
        if welcome_client:
            self.setCurrentIndex(0)
        return filename

    def maybe_create_welcome_client(self):
        """
        Create a welcome tab if there are no tabs.

        Returns
        -------
        client : NotebookClient or None
            The client in the created tab, or None if no tab is created.
        """
        if self.count() == 0:
            welcome = open(WELCOME).read()
            client = NotebookClient(
                self, WELCOME, self.actions, ini_message=welcome)
            self.add_tab(client)
            return client

    def add_tab(self, widget):
        """
        Add tab containing some notebook widget to the tabbed widget.

        Parameters
        ----------
        widget : NotebookClient
            Notebook widget to display in new tab.
        """
        self.clients.append(widget)
        index = self.addTab(widget, widget.get_short_name())
        self.setCurrentIndex(index)
        self.setTabToolTip(index, widget.get_filename())
