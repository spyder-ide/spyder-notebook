# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""Notebook plugin."""

# Stdlib imports
import os
import os.path as osp

# Qt imports
from qtpy import PYQT4, PYSIDE
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QMessageBox, QVBoxLayout, QMenu

# Spyder imports
from spyder.api.plugins import SpyderPluginWidget
from spyder.config.base import _
from spyder.utils import icon_manager as ima
from spyder.utils.qthelpers import (create_action, create_toolbutton,
                                    add_actions, MENU_SEPARATOR)
from spyder.utils.switcher import shorten_paths


# Local imports
from spyder_notebook.widgets.notebooktabwidget import NotebookTabWidget


FILTER_TITLE = _("Jupyter notebooks")
FILES_FILTER = "{} (*.ipynb)".format(FILTER_TITLE)
PACKAGE_PATH = osp.dirname(__file__)
WELCOME = osp.join(PACKAGE_PATH, 'utils', 'templates', 'welcome.html')


class NotebookPlugin(SpyderPluginWidget):
    """IPython Notebook plugin."""

    CONF_SECTION = 'notebook'
    CONF_DEFAULTS = [(CONF_SECTION, {'recent_notebooks': []})]
    focus_changed = Signal()

    def __init__(self, parent, testing=False):
        """Constructor."""
        if testing:
            self.CONF_FILE = False

        SpyderPluginWidget.__init__(self, parent)
        self.testing = testing

        self.fileswitcher_dlg = None
        self.main = parent

        self.recent_notebooks = self.get_option('recent_notebooks', default=[])
        self.recent_notebook_menu = QMenu(_("Open recent"), self)

        layout = QVBoxLayout()

        new_notebook_btn = create_toolbutton(self,
                                             icon=ima.icon('options_more'),
                                             tip=_('Open a new notebook'),
                                             triggered=self.create_new_client)
        menu_btn = create_toolbutton(self, icon=ima.icon('tooloptions'),
                                     tip=_('Options'))

        self.menu_actions = self.get_plugin_actions()
        menu_btn.setMenu(self._options_menu)
        menu_btn.setPopupMode(menu_btn.InstantPopup)
        corner_widgets = {Qt.TopRightCorner: [new_notebook_btn, menu_btn]}
        self.tabwidget = NotebookTabWidget(
            self, menu=self._options_menu, actions=self.menu_actions,
            corner_widgets=corner_widgets)

        self.tabwidget.currentChanged.connect(self.refresh_plugin)

        layout.addWidget(self.tabwidget)
        self.setLayout(layout)

    # ------ SpyderPluginMixin API --------------------------------------------
    def on_first_registration(self):
        """Action to be performed on first plugin registration."""
        self.main.tabify_plugins(self.main.editor, self)

    def update_font(self):
        """Update font from Preferences."""
        # For now we're passing. We need to create an nbextension for
        # this.
        pass

    # ------ SpyderPluginWidget API -------------------------------------------
    def get_plugin_title(self):
        """Return widget title."""
        title = _('Notebook')
        return title

    def get_plugin_icon(self):
        """Return widget icon."""
        return ima.icon('ipython_console')

    def get_focus_widget(self):
        """Return the widget to give focus to."""
        client = self.tabwidget.currentWidget()
        if client is not None:
            return client.notebookwidget

    def closing_plugin(self, cancelable=False):
        """Perform actions before parent main window is closed."""
        for client_index in range(self.tabwidget.count()):
            self.tabwidget.widget(client_index).close()
        self.set_option('recent_notebooks', self.recent_notebooks)
        return True

    def refresh_plugin(self):
        """Refresh tabwidget."""
        nb = None
        if self.tabwidget.count():
            client = self.tabwidget.currentWidget()
            nb = client.notebookwidget
            nb.setFocus()
        else:
            nb = None
        self.update_notebook_actions()

    def get_plugin_actions(self):
        """Return a list of actions related to plugin."""
        create_nb_action = create_action(self,
                                         _("New notebook"),
                                         icon=ima.icon('filenew'),
                                         triggered=self.create_new_client)
        self.save_as_action = create_action(self,
                                            _("Save as..."),
                                            icon=ima.icon('filesaveas'),
                                            triggered=self.save_as)
        open_action = create_action(self,
                                    _("Open..."),
                                    icon=ima.icon('fileopen'),
                                    triggered=self.open_notebook)
        self.open_console_action = create_action(self,
                                                 _("Open console"),
                                                 icon=ima.icon(
                                                         'ipython_console'),
                                                 triggered=self.open_console)
        self.clear_recent_notebooks_action =\
            create_action(self, _("Clear this list"),
                          triggered=self.clear_recent_notebooks)
        # Plugin actions
        self.menu_actions = [create_nb_action, open_action,
                             self.recent_notebook_menu, MENU_SEPARATOR,
                             self.save_as_action, MENU_SEPARATOR,
                             self.open_console_action]
        self.setup_menu_actions()

        return self.menu_actions

    def register_plugin(self):
        """Register plugin in Spyder's main window."""
        super().register_plugin()
        self.focus_changed.connect(self.main.plugin_focus_changed)
        self.ipyconsole = self.main.ipyconsole
        self.tabwidget.maybe_create_welcome_client()
        self.create_new_client()
        self.tabwidget.setCurrentIndex(0)  # bring welcome tab to top

        # Connect to switcher
        self.switcher = self.main.switcher
        self.switcher.sig_mode_selected.connect(self.handle_switcher_modes)
        self.switcher.sig_item_selected.connect(
            self.handle_switcher_selection)

        self.recent_notebook_menu.aboutToShow.connect(self.setup_menu_actions)

    def check_compatibility(self):
        """Check compatibility for PyQt and sWebEngine."""
        message = ''
        value = True
        if PYQT4 or PYSIDE:
            message = _("You are working with Qt4 and in order to use this "
                        "plugin you need to have Qt5.<br><br>"
                        "Please update your Qt and/or PyQt packages to "
                        "meet this requirement.")
            value = False
        return value, message

    # ------ Public API (for clients) -----------------------------------------
    def setup_menu_actions(self):
        """Setup and update the menu actions."""
        self.recent_notebook_menu.clear()
        self.recent_notebooks_actions = []
        if self.recent_notebooks:
            for notebook in self.recent_notebooks:
                name = notebook
                action = \
                    create_action(self,
                                  name,
                                  icon=ima.icon('filenew'),
                                  triggered=lambda v,
                                  path=notebook:
                                      self.create_new_client(filename=path))
                self.recent_notebooks_actions.append(action)
            self.recent_notebooks_actions += \
                [None, self.clear_recent_notebooks_action]
        else:
            self.recent_notebooks_actions = \
                [self.clear_recent_notebooks_action]
        add_actions(self.recent_notebook_menu, self.recent_notebooks_actions)
        self.update_notebook_actions()

    def update_notebook_actions(self):
        """Update actions of the recent notebooks menu."""
        if self.recent_notebooks:
            self.clear_recent_notebooks_action.setEnabled(True)
        else:
            self.clear_recent_notebooks_action.setEnabled(False)
        try:
            client = self.tabwidget.currentWidget()
        except AttributeError:  # tabwidget is not yet constructed
            client = None
        if client:
            if client.get_filename() != WELCOME:
                self.save_as_action.setEnabled(True)
                self.open_console_action.setEnabled(True)
                return
        self.save_as_action.setEnabled(False)
        self.open_console_action.setEnabled(False)

    def add_to_recent(self, notebook):
        """
        Add an entry to recent notebooks.

        We only maintain the list of the 20 most recent notebooks.
        """
        if notebook not in self.recent_notebooks:
            self.recent_notebooks.insert(0, notebook)
            self.recent_notebooks = self.recent_notebooks[:20]

    def clear_recent_notebooks(self):
        """Clear the list of recent notebooks."""
        self.recent_notebooks = []
        self.setup_menu_actions()

    def create_new_client(self, filename=None):
        """Create a new notebook or load a pre-existing one."""
        # Save spyder_pythonpath before creating a client
        # because it's needed by our kernel spec.
        if not self.testing:
            self.set_option('main/spyder_pythonpath',
                            self.main.get_spyder_pythonpath())

        client = self.tabwidget.create_new_client(filename)
        if not self.tabwidget.is_newly_created(client):
            self.add_to_recent(filename)
            self.setup_menu_actions()

    def open_notebook(self, filenames=None):
        """Open a notebook from file."""
        # Save spyder_pythonpath before creating a client
        # because it's needed by our kernel spec.
        if not self.testing:
            self.set_option('main/spyder_pythonpath',
                            self.main.get_spyder_pythonpath())

        filenames = self.tabwidget.open_notebook(filenames)
        for filename in filenames:
            self.add_to_recent(filename)
        self.setup_menu_actions()

    def save_as(self):
        """Save current notebook to different file."""
        self.tabwidget.save_as()

    def open_console(self, client=None):
        """Open an IPython console for the given client or the current one."""
        if not client:
            client = self.tabwidget.currentWidget()
        if self.ipyconsole is not None:
            kernel_id = client.get_kernel_id()
            if not kernel_id:
                QMessageBox.critical(
                    self, _('Error opening console'),
                    _('There is no kernel associated to this notebook.'))
                return
            self.ipyconsole._create_client_for_kernel(kernel_id, None, None,
                                                      None)
            ipyclient = self.ipyconsole.get_current_client()
            ipyclient.allow_rename = False
            self.ipyconsole.rename_client_tab(ipyclient,
                                              client.get_short_name())

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
