# -*- coding: utf-8 -*-
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

# Standard library imports
import os.path as osp

# Third-party imports
from jupyter_core.paths import jupyter_runtime_dir
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QMessageBox, QVBoxLayout

# Spyder imports
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
    Open = 'Open'
    Other = 'Other'


class NotebookMainWidgetRecentNotebooksMenuSections:
    Notebooks = 'Notebooks'
    Clear = 'Clear'


class NotebookMainWidget(PluginMainWidget):

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

        self.recent_notebooks = self.get_conf('recent_notebooks', default=[])
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
        # Corner widgets
        new_notebook_toolbar_action = self.create_toolbutton(
            NotebookMainWidgetToolButtons.NewNotebook,
            icon=self.create_icon('options_more'),
            text=_('Open a new notebook'),
            tip=_('Open a new notebook'),
            triggered=self.create_new_client
        )

        self.add_corner_widget(new_notebook_toolbar_action)

        # Menu actions
        new_notebook_action = self.create_action(
            NotebookMainWidgetActions.NewNotebook,
            text=_("New notebook"),
            icon=self.create_icon('filenew'),
            triggered=self.create_new_client
        )
        open_notebook_action = self.create_action(
            NotebookMainWidgetActions.Open,
            text=_("Open..."),
            icon=self.create_icon('fileopen'),
            triggered=self.open_notebook
        )
        self.save_as_action = self.create_action(
            NotebookMainWidgetActions.SaveAs,
            text=_("Save as..."),
            icon=self.create_icon('filesaveas'),
            triggered=self.save_as
        )
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
        self.clear_recent_notebooks_action = self.create_action(
            NotebookMainWidgetActions.ClearRecentNotebooks,
            text=_("Clear this list"),
            triggered=self.clear_recent_notebooks
        )

        # Submenu
        self.recent_notebooks_menu = self.create_menu(
            NotebookMainWidgetMenus.RecentNotebooks,
            _("Open recent")
        )

        # Options menu
        options_menu = self.get_options_menu()
        for item in [new_notebook_action, open_notebook_action,
                     self.recent_notebooks_menu]:
            self.add_item_to_menu(
                item,
                menu=options_menu,
                section=NotebookMainWidgetOptionsMenuSections.Open,
            )

        for item in [self.save_as_action, self.open_console_action,
                     self.server_info_action]:
            self.add_item_to_menu(
                item,
                menu=options_menu,
                section=NotebookMainWidgetOptionsMenuSections.Other,
            )

        # Context menu for notebooks
        self.tabwidget.actions = [new_notebook_action, open_notebook_action]

    def update_actions(self):
        """Update actions of the options menu."""
        try:
            client = self.tabwidget.currentWidget()
        except AttributeError:  # tabwidget is not yet constructed
            client = None

        if client and not self.tabwidget.is_welcome_client(client):
            self.save_as_action.setEnabled(True)
            self.open_console_action.setEnabled(True)
        else:
            self.save_as_action.setEnabled(False)
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

        self.set_conf('recent_notebooks', self.recent_notebooks)
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

    def update_recent_notebooks_menu(self):
        """Update the recent notebooks menu actions."""
        self.recent_notebooks_menu.clear_actions()
        if self.recent_notebooks:
            for notebook in self.recent_notebooks:
                # Create notebook action
                name = notebook
                action = self.create_action(
                    NotebookMainWidgetActions.RecentNotebook,
                    text=name,
                    icon=self.create_icon('notebook'),
                    register_action=False,
                    triggered=lambda v, path=notebook:
                        self.create_new_client(filename=path)
                )

                # Add action to menu
                self.add_item_to_menu(
                    action,
                    menu=self.recent_notebooks_menu,
                    section=NotebookMainWidgetRecentNotebooksMenuSections.Notebooks,
                )

        self.add_item_to_menu(
            self.clear_recent_notebooks_action,
            menu=self.recent_notebooks_menu,
            section=NotebookMainWidgetRecentNotebooksMenuSections.Clear,
        )

        if self.recent_notebooks:
            self.clear_recent_notebooks_action.setEnabled(True)
        else:
            self.clear_recent_notebooks_action.setEnabled(False)

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
            self.add_to_recent(filename)
        self.update_recent_notebooks_menu()

    def create_new_client(self, filename=None):
        """Create a new notebook or load a pre-existing one."""
        client = self.tabwidget.create_new_client(filename)
        if not self.tabwidget.is_newly_created(client):
            self.add_to_recent(filename)
            self.update_recent_notebooks_menu()

    def add_to_recent(self, notebook):
        """
        Add an entry to recent notebooks.

        We only maintain the list of the 20 most recent notebooks.
        """
        if notebook not in self.recent_notebooks:
            self.recent_notebooks.insert(0, notebook)
            self.recent_notebooks = self.recent_notebooks[:20]

    def save_as(self):
        """Save current notebook to different file."""
        self.tabwidget.save_as()

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

    def clear_recent_notebooks(self):
        """Clear the list of recent notebooks."""
        self.recent_notebooks = []
        self.update_recent_notebooks_menu()
