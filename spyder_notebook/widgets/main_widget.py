# -*- coding: utf-8 -*-
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

# Standard library imports
import os.path as osp
from typing import Optional

# Third-party imports
from jupyter_core.paths import jupyter_runtime_dir
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QMessageBox, QVBoxLayout

# Spyder imports
from spyder.api.plugins import Plugins
from spyder.api.widgets.main_widget import PluginMainWidget
from spyder.config.gui import is_dark_interface

# Local imports
from spyder_notebook.utils.localization import _
from spyder_notebook.utils.servermanager import ServerManager
from spyder_notebook.widgets.notebooktabwidget import NotebookTabWidget
from spyder_notebook.widgets.serverinfo import ServerInfoDialog


class NotebookMainWidgetToolButtons:
    NewNotebook = 'New notebook'


class NotebookMainWidgetActions:
    NewNotebook = 'New notebook'
    SaveAs = 'Save as'
    Open = 'Open'
    OpenConsole = 'Open console'
    ServerInfo = 'Server info'
    ClearRecentNotebooks = 'Clear recent notebooks'
    RecentNotebook = 'Recent notebook'


class NotebookMainWidgetMenus:
    RecentNotebooks = 'Recent notebooks'


class NotebookMainWidgetOptionsMenuSections:
    Main = 'Main'


class NotebookMainWidgetRecentNotebooksMenuSections:
    Notebooks = 'Notebooks'
    Clear = 'Clear'


class NotebookMainWidget(PluginMainWidget):

    sig_new_recent_file = Signal(str)
    """
    This signal is emitted when a file is opened or got a new name.

    Parameters
    ----------
    filename: str
        The name of the opened file. If the file is renamed, then this should
        be the new name.
    """

    sig_open_console_requested = Signal(str, str)
    """
    Request to open an IPython console associated to a notebook.

    Parameters
    -----------
    connection_file: str
        Name of the connection file for the kernel to open a console for.
    tab_name: str
        Tab name to set for the created console.
    """

    def __init__(self, name, plugin, parent):
        """Widget constructor."""
        super().__init__(name, plugin, parent)

        self.server_manager = ServerManager(self.dark_theme)

        # Tab widget
        self.tabwidget = NotebookTabWidget(
            self,
            self.server_manager,
            dark_theme=self.dark_theme
        )
        self.tabwidget.currentChanged.connect(self.refresh_plugin)

        # Widget layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabwidget)
        self.setLayout(layout)

    # ---- PluginMainWidget API
    # ------------------------------------------------------------------------
    def get_focus_widget(self):
        """Return the widget to give focus to."""
        client = self.tabwidget.currentWidget()
        if client is not None:
            return client.notebookwidget

    def get_title(self):
        """Define the title of the widget."""
        return _('Notebook')

    def setup(self):
        """Perform the setup of plugin's main menu and signals."""
        self.open_console_action = self.create_action(
            NotebookMainWidgetActions.OpenConsole,
            text=_("Open console"),
            icon=self.create_icon('ipython_console'),
            triggered=self.open_console
        )
        self.server_info_action = self.create_action(
            NotebookMainWidgetActions.ServerInfo,
            text=_('Server info...'),
            icon=self.create_icon('log'),
            triggered=self.view_servers
        )

        # Options menu
        options_menu = self.get_options_menu()
        for item in [self.open_console_action, self.server_info_action]:
            self.add_item_to_menu(
                item,
                menu=options_menu,
                section=NotebookMainWidgetOptionsMenuSections.Main,
            )

        # Register shortcuts for file actions defined in Applications plugin
        for shortcut_name in [
            'New file',
            'Open file',
            'Open last closed',
            'Save file',
            'Save all',
            'Save as',
            'Close file 1',
            'Close file 2'
        ]:
            # The shortcut has the same name as the action, except for
            # "Close file" which has two shortcuts associated to it
            if shortcut_name.startswith('Close file'):
                action_id = 'Close file'
            else:
                action_id = shortcut_name

            action = self.get_action(action_id, plugin=Plugins.Application)
            self.register_shortcut_for_widget(
                name=shortcut_name,
                triggered=action.trigger,
                context='main'
            )

    def update_actions(self):
        """Update actions of the options menu."""
        try:
            client = self.tabwidget.currentWidget()
        except AttributeError:  # tabwidget is not yet constructed
            client = None

        if client and not self.tabwidget.is_welcome_client(client):
            self.open_console_action.setEnabled(True)
        else:
            self.open_console_action.setEnabled(False)

    def on_close(self):
        """
        Perform actions before parent main window is closed.

        This function closes all tabs, shuts down all notebook server and
        stores the file names of all opened notebooks that are not temporary
        and all notebooks in the 'Open recent' menu in Spyder's config.
        """
        opened_notebooks = []
        for client_index in range(self.tabwidget.count()):
            client = self.tabwidget.widget(client_index)
            if (not self.tabwidget.is_welcome_client(client)
                    and not self.tabwidget.is_newly_created(client)):
                opened_notebooks.append(client.filename)
            client.close()

        self.set_conf('opened_notebooks', opened_notebooks)
        self.server_manager.shutdown_all_servers()

    # ---- Public API
    # ------------------------------------------------------------------------
    @property
    def dark_theme(self):
        """Whether to use the dark theme for notebooks (bool)."""
        theme_config = self.get_conf('theme', default='same as spyder')
        if theme_config == 'same as spyder':
            return is_dark_interface()
        elif theme_config == 'dark':
            return True
        elif theme_config == 'light':
            return False
        else:
            raise RuntimeError('theme config corrupted, value = {}'
                               .format(theme_config))

    def refresh_plugin(self):
        """Refresh tabwidget."""
        nb = None
        if self.tabwidget.count():
            client = self.tabwidget.currentWidget()
            nb = client.notebookwidget
            nb.setFocus()
        else:
            nb = None

    def open_previous_session(self):
        """Open notebooks left open in the previous session."""
        filenames = self.get_conf('opened_notebooks')
        if filenames:
            self.open_notebook(filenames)
        else:
            self.tabwidget.maybe_create_welcome_client()
            self.create_new_client()
            self.tabwidget.setCurrentIndex(0)  # bring welcome tab to top

    def open_notebook(self, filenames=None):
        """Open a notebook from file."""
        filenames = self.tabwidget.open_notebook(filenames)
        for filename in filenames:
            self.sig_new_recent_file.emit(filename)

    def open_last_closed_notebook(self) -> None:
        """
        Reopens the notebook in the last closed tab.
        """
        self.tabwidget.open_last_closed_notebook()

    def create_new_client(self, filename=None):
        """Create a new notebook or load a pre-existing one."""
        client = self.tabwidget.create_new_client(filename)
        if not self.tabwidget.is_newly_created(client):
            self.sig_new_recent_file.emit(filename)

    def save_notebook(self) -> None:
        """
        Save current notebook.
        """
        client = self.tabwidget.currentWidget()
        self.tabwidget.save_notebook(client)

    def save_all(self) -> None:
        """
        Save all opened notebooks.
        """
        for client_index in range(self.tabwidget.count()):
            client = self.tabwidget.widget(client_index)
            self.tabwidget.save_notebook(client)

    def save_as(self, close_after_save=True):
        """
        Save current notebook to different file.

        If `close_after_save` is True (the default), then close the current
        tab and open a new tab under the new name. Otherwise, open a new tab
        while leaving the current tab open (the "Save copy as" action).
        """
        old_filename = self.tabwidget.currentWidget()
        new_filename = self.tabwidget.save_as(
            close_after_save=close_after_save
        )
        if old_filename != new_filename:
            self.sig_new_recent_file.emit(new_filename)

    def close_notebook(self) -> None:
        """
        Close current notebook.
        """
        self.tabwidget.close_client()

    def close_all(self) -> None:
        """
        Close all notebooks.

        Go through all tabs, skip any tabs with the welcome message and close
        all other tabs. The tabs are traversed in reverse order so that the
        index does not change when tabs are removed.
        """
        for client_index in reversed(range(self.tabwidget.count())):
            client = self.tabwidget.widget(client_index)
            if not self.tabwidget.is_welcome_client(client):
                self.tabwidget.close_client(client_index)

    def open_console(self, client=None):
        """Open an IPython console for the given client or the current one."""
        if not client:
            client = self.tabwidget.currentWidget()

        kernel_id = client.get_kernel_id()
        if not kernel_id:
            QMessageBox.critical(
                self,
                _('Error opening console'),
                _('There is no kernel associated to this notebook.')
            )
            return

        connection_file = f'kernel-{kernel_id}.json'
        connection_file = osp.join(jupyter_runtime_dir(), connection_file)
        self.sig_open_console_requested.emit(
            connection_file,
            client.get_short_name()
        )

    def view_servers(self):
        """Display server info."""
        dialog = ServerInfoDialog(self.server_manager.servers, parent=self)
        dialog.show()

    def get_current_filename(self) -> Optional[str]:
        """
        Get file name of currently displayed notebook.
        """
        client = self.tabwidget.currentWidget()
        if self.tabwidget.is_welcome_client(client):
            return None
        else:
            return client.get_filename()

    def current_file_is_temporary(self) -> bool:
        """
        Return whether currently displayed file is a temporary file.
        """
        client = self.tabwidget.currentWidget()
        return self.tabwidget.is_newly_created(client)
