# -*- coding: utf-8 -*-
#
# Copyright © 2014 The Spyder development team
# Licensed under the terms of the MIT License
# (see spyderlib/__init__.py for details)

"""
Jupyter Notebook plugin
"""

# Stdlib imports
import os.path as osp
import subprocess
import sys
import tempfile

# Qt imports
from qtpy.QtWidgets import QApplication, QMessageBox, QVBoxLayout
from qtpy.QtCore import Qt, Signal

# Third-party imports
import nbformat

# Spyder imports
from spyder.config.base import _
from spyder.utils import icon_manager as ima
from spyder.utils.qthelpers import create_action
from spyder.widgets.tabs import Tabs
from spyder.plugins import SpyderPluginWidget
from spyder.py3compat import to_text_string

# Local imports
from .utils.nbopen import nbopen, NBServerError
from .widgets.client import NotebookClient


NOTEBOOK_TMPDIR = tempfile.gettempdir()


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
        self.tabwidget = Tabs(self, self.menu_actions)
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
        font = self.get_plugin_font()
        for client in self.clients:
            client.set_font(font)

    #------ SpyderPluginWidget API --------------------------------------------
    def get_plugin_title(self):
        """Return widget title"""
        title = _('IPython Notebook')
        nbname = self.get_current_client_name(short=True)
        if nbname:
            title += ' - ' + to_text_string(nbname)
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
        self.update_plugin_title.emit()

    def get_plugin_actions(self):
        """Return a list of actions related to plugin"""
        create_nb_action = create_action(self,
                                         _("Open a new notebook"),
                                         None,
                                         triggered=self.create_new_client)

        # Plugin actions
        self.menu_actions = [create_nb_action]
        return self.menu_actions

    def register_plugin(self):
        """Register plugin in Spyder's main window"""
        self.focus_changed.connect(self.main.plugin_focus_changed)
        self.main.add_dockwidget(self)
        self.create_new_client(give_focus=False)

    #------ Public API (for clients) ------------------------------------------
    def get_clients(self):
        """Return notebooks list"""
        return [cl for cl in self.clients if isinstance(nb, NotebookClient)]

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
            nb_name = 'Untitled' + str(self.untitled_num) + '.ipynb'
            name = osp.join(NOTEBOOK_TMPDIR, nb_name)
            nb = nbformat.v4.new_notebook()
            nbformat.write(nb, nb_name)

        client = NotebookClient(self, name)
        self.add_tab(client)

        # Open the notebook with nbopen and get the url we need to render
        try:
            url = nbopen(nb_name)
        except (subprocess.CalledProcessError, NBServerError):
            QMessageBox.critical(
                self,
                _("Server error"),
                _("The Jupyter Notebook server failed to start or it is "
                  "taking too much time to do it. Please start it in a "
                  "system terminal with the command 'jupyter notebook' to "
                  "check for errors."))
            return

        self.untitled_num += 1
        client.set_url(url)

    def close_client(self, index=None, notebook=None):
        """Close client tab from index or widget (or close current tab)"""
        if not self.tabwidget.count():
            return
        if notebook is not None:
            index = self.tabwidget.indexOf(notebook)
        if index is None and notebook is None:
            index = self.tabwidget.currentIndex()
        if index is not None:
            notebook = self.tabwidget.widget(index)

        # TODO: Eliminate the notebook from disk if it's an Untitled one
        notebook.close()

        # Note: notebook index may have changed after closing related widgets
        self.tabwidget.removeTab(self.tabwidget.indexOf(notebook))
        self.clients.remove(notebook)

        self.update_plugin_title.emit()

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
        self.update_plugin_title.emit()