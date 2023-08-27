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
    OPTIONAL = [Plugins.IPythonConsole]
    TABIFY = [Plugins.Editor]
    CONF_SECTION = NAME
    CONF_DEFAULTS = CONF_DEFAULTS
    CONF_VERSION = CONF_VERSION
    WIDGET_CLASS = NotebookMainWidget
    CONF_WIDGET_CLASS = NotebookConfigPage

    # Action "Switch to notebook" gives focus to the plugin
    RAISE_AND_FOCUS = True

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

    @on_plugin_teardown(plugin=Plugins.Preferences)
    def on_preferences_teardown(self):
        preferences = self.get_plugin(Plugins.Preferences)
        preferences.deregister_plugin_preferences(self)

    @on_plugin_teardown(plugin=Plugins.IPythonConsole)
    def on_ipyconsole_teardown(self):
        self.get_widget().sig_open_console_requested.disconnect(
            self._open_console)

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
