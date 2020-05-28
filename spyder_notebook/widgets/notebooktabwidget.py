# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""File implementing NotebookTabWidget."""

# Standard library imports
import os.path as osp
import sys

# Spyder imports
from spyder.widgets.tabs import Tabs

# Local imports
from spyder_notebook.widgets.client import NotebookClient


# Path to HTML file with welcome message
PACKAGE_PATH = osp.join(osp.dirname(__file__), '..')
WELCOME = osp.join(PACKAGE_PATH, 'utils', 'templates', 'welcome.html')


class NotebookTabWidget(Tabs):
    """
    Tabbed widget whose tabs display notebooks.

    This is the main widget of the notebook plugin.

    Attributes
    ----------
    actions : list of (QAction or QMenu or None) or None
    clients : list of NotebookClient
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

        if not sys.platform == 'darwin':
            # Don't set document mode to true on OSX because it generates
            # a crash when the console is detached from the main window
            # Fixes spyder-ide/spyder#561
            self.setDocumentMode(True)

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
