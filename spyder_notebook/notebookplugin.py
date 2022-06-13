# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""Notebook plugin."""

# Stdlib imports
import os
import os.path as osp

# Qt imports
from qtpy.QtCore import Signal
from qtpy.QtGui import QIcon

# Spyder imports
from spyder.api.plugins import Plugins, SpyderDockablePlugin
from spyder.api.plugin_registration.decorators import (
    on_plugin_available, on_plugin_teardown)
from spyder.utils.switcher import shorten_paths

# Local imports
from spyder_notebook.config import CONF_DEFAULTS, CONF_VERSION
from spyder_notebook.confpage import NotebookConfigPage
from spyder_notebook.widgets.main_widget import NotebookMainWidget
from spyder_notebook.utils.localization import _


FILTER_TITLE = _("Jupyter notebooks")
FILES_FILTER = "{} (*.ipynb)".format(FILTER_TITLE)
PACKAGE_PATH = osp.dirname(__file__)


class NotebookPlugin(SpyderDockablePlugin):
    """Spyder Notebook plugin."""

    NAME = 'notebook'
    REQUIRES = [Plugins.Preferences]
    OPTIONAL = [Plugins.IPythonConsole]
    TABIFY = [Plugins.Editor]
    CONF_SECTION = NAME
    CONF_DEFAULTS = CONF_DEFAULTS
    CONF_VERSION = CONF_VERSION
    WIDGET_CLASS = NotebookMainWidget
    CONF_WIDGET_CLASS = NotebookConfigPage

    # ---- Signals
    # ------------------------------------------------------------------------
    focus_changed = Signal()

    # ---- SpyderDockablePlugin API
    # ------------------------------------------------------------------------
    @staticmethod
    def get_name():
        """Return plugin name."""
        title = _('Notebook')
        return title

    def get_description(self):
        """Return the plugin description."""
        return _("Work with Jupyter notebooks inside Spyder.")

    def get_icon(self):
        """Return plugin icon."""
        return self.create_icon('notebook')

    def on_initialize(self):
        """Register plugin in Spyder's main window."""
        self.focus_changed.connect(self.main.plugin_focus_changed)

        # Connect to switcher
        self.switcher = self.main.switcher
        self.switcher.sig_mode_selected.connect(self.handle_switcher_modes)
        self.switcher.sig_item_selected.connect(
            self.handle_switcher_selection)

    @on_plugin_available(plugin=Plugins.Preferences)
    def on_preferences_available(self):
        preferences = self.get_plugin(Plugins.Preferences)
        preferences.register_plugin_preferences(self)

    @on_plugin_available(plugin=Plugins.IPythonConsole)
    def on_ipyconsole_available(self):
        self.get_widget().sig_open_console_requested.connect(
            self.open_console)

    @on_plugin_teardown(plugin=Plugins.Preferences)
    def on_preferences_teardown(self):
        preferences = self.get_plugin(Plugins.Preferences)
        preferences.deregister_plugin_preferences(self)

    @on_plugin_teardown(plugin=Plugins.IPythonConsole)
    def on_ipyconsole_teardown(self):
        self.get_widget().sig_open_console_requested.disconnect(
            self.open_console)

    def on_mainwindow_visible(self):
        self.get_widget().open_previous_session()

    # ------ Public API -------------------------------------------------------
    def open_console(self, kernel_id, tab_name):
        """Open an IPython console as requested."""
        ipyconsole = self.get_plugin(Plugins.IPythonConsole)
        ipyconsole.get_widget()._create_client_for_kernel(
            kernel_id, None, None, None)
        ipyclient = ipyconsole.get_current_client()
        ipyclient.allow_rename = False
        ipyconsole.get_widget().rename_client_tab(ipyclient, tab_name)

    # ------ Public API (for FileSwitcher) ------------------------------------
    def handle_switcher_modes(self, mode):
        """
        Populate switcher with opened notebooks.

        List the file names of the opened notebooks with their directories in
        the switcher. Only handle file mode, where `mode` is empty string.
        """
        if mode != '':
            return

        clients = [self.tabwidget.widget(i)
                   for i in range(self.tabwidget.count())]
        paths = [client.get_filename() for client in clients]
        is_unsaved = [False for client in clients]
        short_paths = shorten_paths(paths, is_unsaved)
        icon = QIcon(os.path.join(PACKAGE_PATH, 'images', 'icon.svg'))
        section = self.get_plugin_title()

        for path, short_path, client in zip(paths, short_paths, clients):
            title = osp.basename(path)
            description = osp.dirname(path)
            if len(path) > 75:
                description = short_path
            is_last_item = (client == clients[-1])
            self.switcher.add_item(
                title=title, description=description, icon=icon,
                section=section, data=client, last_item=is_last_item)

    def handle_switcher_selection(self, item, mode, search_text):
        """
        Handle user selecting item in switcher.

        If the selected item is not in the section of the switcher that
        corresponds to this plugin, then ignore it. Otherwise, switch to
        selected item in notebook plugin and hide the switcher.
        """
        if item.get_section() != self.get_plugin_title():
            return

        client = item.get_data()
        index = self.tabwidget.indexOf(client)
        self.tabwidget.setCurrentIndex(index)
        self.switch_to_plugin()
        self.switcher.hide()
