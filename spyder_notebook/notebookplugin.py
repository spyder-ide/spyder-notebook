# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Jupyter Notebook plugin."""

# Standard library imports
import os.path as osp
import subprocess
import sys
import tempfile

# Third party imports
from qtpy.compat import getsavefilename
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QApplication, QMenu, QMessageBox, QVBoxLayout
from spyder.config.base import _
from spyder.plugins import SpyderPluginWidget
from spyder.utils import icon_manager as ima
from spyder.utils.qthelpers import (add_actions, create_action,
                                    create_toolbutton)
from spyder.widgets.tabs import Tabs
import nbformat

# Local relative imports
from .utils.nbopen import NBServerError, nbopen
from .widgets.client import NotebookClient

NOTEBOOK_TMPDIR = tempfile.gettempdir()
FILTER_TITLE = _("Jupyter notebooks")
FILES_FILTER = "{} (*.ipynb)".format(FILTER_TITLE)


class NotebookPlugin(SpyderPluginWidget):
    """IPython Notebook plugin."""

    CONF_SECTION = 'notebook'
    focus_changed = Signal()

    def __init__(self, parent):
        SpyderPluginWidget.__init__(self, parent)

        self.tabwidget = None
        self.menu_actions = None

        self.main = parent

        self.clients = []
        self.untitled_num = 0

        # Initialize plugin
        self.initialize_plugin()

        layout = QVBoxLayout()

        new_notebook_btn = create_toolbutton(self,
                                             icon=ima.icon('project_expanded'),
                                             tip=_('Open a new notebook'),
                                             triggered=self.create_new_client)
        menu_btn = create_toolbutton(self, icon=ima.icon('tooloptions'),
                                     tip=_('Options'))
        self.menu = QMenu(self)
        menu_btn.setMenu(self.menu)
        menu_btn.setPopupMode(menu_btn.InstantPopup)
        add_actions(self.menu, self.menu_actions)
        corner_widgets = {Qt.TopRightCorner: [new_notebook_btn, menu_btn]}
        self.tabwidget = Tabs(self, menu=self.menu, actions=self.menu_actions,
                              corner_widgets=corner_widgets)

        if hasattr(self.tabwidget, 'setDocumentMode') \
           and not sys.platform == 'darwin':
            # Don't set document mode to true on OSX because it generates
            # a crash when the console is detached from the main window
            # Fixes Issue 561
            self.tabwidget.setDocumentMode(True)
        self.tabwidget.currentChanged.connect(self.refresh_plugin)
        self.tabwidget.move_data.connect(self.move_tab)

        self.tabwidget.set_close_function(self.close_client)

        layout.addWidget(self.tabwidget)
        self.setLayout(layout)

    #------ SpyderPluginMixin API ---------------------------------------------
    def on_first_registration(self):
        """Action to be performed on first plugin registration"""
        self.main.tabify_plugins(self.main.editor, self)

    def update_font(self):
        """Update font from Preferences"""
        # For now we're passing. We need to create an nbextension for
        # this.
        pass

    #------ SpyderPluginWidget API --------------------------------------------
    def get_plugin_title(self):
        """Return widget title"""
        title = _('Jupyter Notebook')
        return title

    def get_plugin_icon(self):
        """Return widget icon"""
        return ima.icon('ipython_console')

    def get_focus_widget(self):
        """
        Return the widget to give focus to when
        this plugin's dockwidget is raised on top-level
        """
        client = self.tabwidget.currentWidget()
        if client is not None:
            return client.notebookwidget

    def closing_plugin(self, cancelable=False):
        """Perform actions before parent main window is closed"""
        for cl in self.clients:
            cl.close()
        return True

    def refresh_plugin(self):
        """Refresh tabwidget"""
        nb = None
        if self.tabwidget.count():
            client = self.tabwidget.currentWidget()
            nb = client.notebookwidget
            nb.setFocus()
        else:
            nb = None

    def get_plugin_actions(self):
        """Return a list of actions related to plugin"""
        create_nb_action = create_action(self,
                                         _("Open a new notebook"),
                                         icon=ima.icon('filenew'),
                                         triggered=self.create_new_client)
        save_as_action = create_action(self,
                                       _("Save as..."),
                                       icon=ima.icon('filesaveas'),
                                       triggered=self.save_as)
        # Plugin actions
        self.menu_actions = [create_nb_action, save_as_action]
        return self.menu_actions

    def register_plugin(self):
        """Register plugin in Spyder's main window"""
        self.focus_changed.connect(self.main.plugin_focus_changed)
        self.main.add_dockwidget(self)
        self.create_new_client(give_focus=False)

    #------ Public API (for clients) ------------------------------------------
    def get_clients(self):
        """Return notebooks list"""
        return [cl for cl in self.clients if isinstance(cl, NotebookClient)]

    def get_focus_client(self):
        """Return current notebook with focus, if any"""
        widget = QApplication.focusWidget()
        for client in self.get_clients():
            if widget is client or widget is client.notebookwidget:
                return client

    def get_current_client(self):
        """Return the currently selected notebook"""
        try:
            client = self.tabwidget.currentWidget()
        except AttributeError:
            client = None
        if client is not None:
            return client

    def get_current_client_name(self, short=False):
        client = self.get_current_client()
        if client:
            if short:
                return client.get_short_name()
            else:
                return client.get_name()

    def create_new_client(self, name=None, give_focus=True):
        """Create a new notebook or load a pre-existing one"""
        # Generate the notebook name (in case of a new one)
        if not name:
            nb_name = 'untitled' + str(self.untitled_num) + '.ipynb'
            name = osp.join(NOTEBOOK_TMPDIR, nb_name)
            nb_contents = nbformat.v4.new_notebook()
            nbformat.write(nb_contents, name)
            self.untitled_num += 1

        client = NotebookClient(self, name)
        self.add_tab(client)

        # Open the notebook with nbopen and get the url we need to render
        try:
            server_info = nbopen(name)
        except (subprocess.CalledProcessError, NBServerError):
            QMessageBox.critical(
                self,
                _("Server error"),
                _("The Jupyter Notebook server failed to start or it is "
                  "taking too much time to do it. Please start it in a "
                  "system terminal with the command 'jupyter notebook' to "
                  "check for errors."))
            return

        client.register(server_info)
        client.load_notebook()

    def close_client(self, index=None, client=None):
        """Close client tab from index or widget (or close current tab)"""
        if not self.tabwidget.count():
            return
        if client is not None:
            index = self.tabwidget.indexOf(client)
        if index is None and client is None:
            index = self.tabwidget.currentIndex()
        if index is not None:
            client = self.tabwidget.widget(index)

        # TODO: Eliminate the notebook from disk if it's an Untitled one
        client.close()

        # Note: notebook index may have changed after closing related widgets
        self.tabwidget.removeTab(self.tabwidget.indexOf(client))
        self.clients.remove(client)

    def save_as(self):
        """Save notebook as..."""
        current_client = self.get_current_client()
        current_client.save()
        original_path = current_client.get_name()
        original_name = osp.basename(original_path)
        filename, _selfilter = getsavefilename(self, _("Save notebook"),
                                       original_name, FILES_FILTER)
        if filename:
            nb_contents = nbformat.read(original_path, as_version=4)
            nbformat.write(nb_contents, filename)
            self.close_client()
            self.create_new_client(name=filename)

    #------ Public API (for tabs) ---------------------------------------------
    def add_tab(self, widget):
        """Add tab"""
        self.clients.append(widget)
        index = self.tabwidget.addTab(widget, widget.get_short_name())
        self.tabwidget.setCurrentIndex(index)
        self.tabwidget.setTabToolTip(index, widget.get_name())
        if self.dockwidget and not self.ismaximized:
            self.dockwidget.setVisible(True)
            self.dockwidget.raise_()
        self.activateWindow()
        widget.notebookwidget.setFocus()

    def move_tab(self, index_from, index_to):
        """
        Move tab (tabs themselves have already been moved by the tabwidget)
        """
        client = self.clients.pop(index_from)
        self.clients.insert(index_to, client)
