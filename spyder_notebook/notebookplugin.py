# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""Notebook plugin."""

# Standard library imports
import logging
import os.path as osp

# Spyder imports
from spyder.api.plugins import Plugins, SpyderDockablePlugin
from spyder.api.plugin_registration.decorators import (
    on_plugin_available, on_plugin_teardown)
from spyder.plugins.switcher.utils import shorten_paths

# Local imports
from spyder_notebook.config import CONF_DEFAULTS, CONF_VERSION
from spyder_notebook.confpage import NotebookConfigPage
from spyder_notebook.widgets.main_widget import NotebookMainWidget
from spyder_notebook.utils.localization import _

logger = logging.getLogger(__name__)


class NotebookPlugin(SpyderDockablePlugin):
    """Spyder Notebook plugin."""

    NAME = 'notebook'
    REQUIRES = [Plugins.Preferences]
    OPTIONAL = [Plugins.IPythonConsole, Plugins.Switcher]
    TABIFY = [Plugins.Editor]
    CONF_SECTION = NAME
    CONF_DEFAULTS = CONF_DEFAULTS
    CONF_VERSION = CONF_VERSION
    WIDGET_CLASS = NotebookMainWidget
    CONF_WIDGET_CLASS = NotebookConfigPage

    # ---- SpyderDockablePlugin API
    # ------------------------------------------------------------------------
    @staticmethod
    def get_name():
        """Return plugin name."""
        title = _('Notebook')
        return title

    @staticmethod
    def get_description():
        """Return the plugin description."""
        return _("Work with Jupyter notebooks inside Spyder.")

    @classmethod
    def get_icon(cls):
        """Return plugin icon."""
        return cls.create_icon('notebook')

    def on_initialize(self):
        """Set up the plugin; does nothing."""
        pass

    @on_plugin_available(plugin=Plugins.Preferences)
    def on_preferences_available(self):
        preferences = self.get_plugin(Plugins.Preferences)
        preferences.register_plugin_preferences(self)

    @on_plugin_available(plugin=Plugins.IPythonConsole)
    def on_ipyconsole_available(self):
        self.get_widget().sig_open_console_requested.connect(
            self._open_console)

    @on_plugin_available(plugin=Plugins.Switcher)
    def on_switcher_available(self):
        switcher = self.get_plugin(Plugins.Switcher)
        switcher.sig_mode_selected.connect(self._handle_switcher_modes)
        switcher.sig_item_selected.connect(self._handle_switcher_selection)

    @on_plugin_teardown(plugin=Plugins.Preferences)
    def on_preferences_teardown(self):
        preferences = self.get_plugin(Plugins.Preferences)
        preferences.deregister_plugin_preferences(self)

    @on_plugin_teardown(plugin=Plugins.IPythonConsole)
    def on_ipyconsole_teardown(self):
        self.get_widget().sig_open_console_requested.disconnect(
            self._open_console)

    @on_plugin_teardown(plugin=Plugins.Switcher)
    def on_switcher_teardown(self):
        switcher = self.get_plugin(Plugins.Switcher)
        switcher.sig_mode_selected.disconnect(self._handle_switcher_modes)
        switcher.sig_item_selected.disconnect(self._handle_switcher_selection)

    def on_mainwindow_visible(self):
        self.get_widget().open_previous_session()

    # ------ Public API -------------------------------------------------------
    def open_notebook(self, filenames=None):
        self.get_widget().open_notebook(filenames)

    # ------ Private API ------------------------------------------------------
    def _open_console(self, connection_file, tab_name):
        """Open an IPython console as requested."""
        logger.info(f'Opening console with {connection_file=}')
        ipyconsole = self.get_plugin(Plugins.IPythonConsole)
        ipyconsole.create_client_for_kernel(connection_file)
        ipyclient = ipyconsole.get_current_client()
        ipyclient.allow_rename = False
        ipyconsole.rename_client_tab(ipyclient, tab_name)

    def _handle_switcher_modes(self, mode):
        """
        Populate switcher with opened notebooks.

        List the file names of the opened notebooks with their directories in
        the switcher. Only handle file mode, where `mode` is empty string.
        """
        if mode != '':
            return

        tabwidget = self.get_widget().tabwidget
        clients = [tabwidget.widget(i) for i in range(tabwidget.count())]
        paths = [client.get_filename() for client in clients]
        is_unsaved = [False for client in clients]
        short_paths = shorten_paths(paths, is_unsaved)
        icon = self.create_icon('notebook')
        section = self.get_name()
        switcher = self.get_plugin(Plugins.Switcher)

        for path, short_path, client in zip(paths, short_paths, clients):
            title = osp.basename(path)
            description = osp.dirname(path)
            if len(path) > 75:
                description = short_path
            is_last_item = (client == clients[-1])

            switcher.add_item(
                title=title,
                description=description,
                icon=icon,
                section=section,
                data=client,
                last_item=is_last_item
            )

    def _handle_switcher_selection(self, item, mode, search_text):
        """
        Handle user selecting item in switcher.

        If the selected item is not in the section of the switcher that
        corresponds to this plugin, then ignore it. Otherwise, switch to
        selected item in notebook plugin and hide the switcher.
        """
        if item.get_section() != self.get_name():
            return

        client = item.get_data()
        tabwidget = self.get_widget().tabwidget
        tabwidget.setCurrentIndex(tabwidget.indexOf(client))
        self.switch_to_plugin()
        switcher = self.get_plugin(Plugins.Switcher)
        switcher.hide()
