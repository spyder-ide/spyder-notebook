# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""Notebook plugin."""

# Stdlib imports
import os
import os.path as osp
import subprocess
import sys

# Qt imports
from qtpy import PYQT4, PYSIDE
from qtpy.compat import getsavefilename, getopenfilenames
from qtpy.QtCore import Qt, QEventLoop, QTimer, Signal
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QApplication, QMessageBox, QVBoxLayout, QMenu

# Third-party imports
import nbformat

# Spyder imports
from spyder.api.plugins import SpyderPluginWidget
from spyder.config.base import _
from spyder.utils import icon_manager as ima
from spyder.utils.programs import get_temp_dir
from spyder.utils.qthelpers import (create_action, create_toolbutton,
                                    add_actions, MENU_SEPARATOR)
from spyder.utils.switcher import shorten_paths
from spyder.widgets.tabs import Tabs


# Local imports
from .utils.nbopen import nbopen, NBServerError
from .widgets.client import NotebookClient


NOTEBOOK_TMPDIR = osp.join(get_temp_dir(), 'notebooks')
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
        self.tabwidget = None
        self.menu_actions = None

        self.main = parent

        self.clients = []
        self.untitled_num = 0
        self.recent_notebooks = self.get_option('recent_notebooks', default=[])
        self.recent_notebook_menu = QMenu(_("Open recent"), self)

        layout = QVBoxLayout()

        new_notebook_btn = create_toolbutton(self,
                                             icon=ima.icon('options_more'),
                                             tip=_('Open a new notebook'),
                                             triggered=self.create_new_client)
        menu_btn = create_toolbutton(self, icon=ima.icon('tooloptions'),
                                     tip=_('Options'))

        menu_btn.setMenu(self._options_menu)
        menu_btn.setPopupMode(menu_btn.InstantPopup)
        corner_widgets = {Qt.TopRightCorner: [new_notebook_btn, menu_btn]}
        self.tabwidget = Tabs(self, menu=self._options_menu,
                              actions=self.menu_actions,
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
        for cl in self.clients:
            cl.close()
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
        super(NotebookPlugin, self).register_plugin()
        self.focus_changed.connect(self.main.plugin_focus_changed)
        self.ipyconsole = self.main.ipyconsole
        self.create_new_client(give_focus=False)

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
        client = self.get_current_client()
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

    def get_clients(self):
        """Return notebooks list."""
        return [cl for cl in self.clients if isinstance(cl, NotebookClient)]

    def get_focus_client(self):
        """Return current notebook with focus, if any."""
        widget = QApplication.focusWidget()
        for client in self.get_clients():
            if widget is client or widget is client.notebookwidget:
                return client

    def get_current_client(self):
        """Return the currently selected notebook."""
        try:
            client = self.tabwidget.currentWidget()
        except AttributeError:
            client = None
        if client is not None:
            return client

    def get_current_nbwidget(self):
        """Return the notebookwidget of the current client."""
        client = self.get_current_client()
        if client is not None:
            return client.notebookwidget

    def get_current_client_name(self, short=False):
        """Get the current client name."""
        client = self.get_current_client()
        if client:
            if short:
                return client.get_short_name()
            else:
                return client.get_filename()

    def create_new_client(self, filename=None, give_focus=True):
        """Create a new notebook or load a pre-existing one."""
        # Generate the notebook name (in case of a new one)
        if not filename:
            if not osp.isdir(NOTEBOOK_TMPDIR):
                os.makedirs(NOTEBOOK_TMPDIR)
            nb_name = 'untitled' + str(self.untitled_num) + '.ipynb'
            filename = osp.join(NOTEBOOK_TMPDIR, nb_name)
            nb_contents = nbformat.v4.new_notebook()
            nbformat.write(nb_contents, filename)
            self.untitled_num += 1

        # Save spyder_pythonpath before creating a client
        # because it's needed by our kernel spec.
        if not self.testing:
            self.set_option('main/spyder_pythonpath',
                            self.main.get_spyder_pythonpath())

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
            self.create_welcome_client()
            return

        welcome_client = self.create_welcome_client()
        client = NotebookClient(self, filename)
        self.add_tab(client)
        if NOTEBOOK_TMPDIR not in filename:
            self.add_to_recent(filename)
            self.setup_menu_actions()
        client.register(server_info)
        client.load_notebook()
        if welcome_client and not self.testing:
            self.tabwidget.setCurrentIndex(0)

    def close_client(self, index=None, client=None, save=False):
        """
        Close client tab from index or widget (or close current tab).

        The notebook is saved if `save` is `False`.
        """
        if not self.tabwidget.count():
            return
        if client is not None:
            index = self.tabwidget.indexOf(client)
        if index is None and client is None:
            index = self.tabwidget.currentIndex()
        if index is not None:
            client = self.tabwidget.widget(index)

        is_welcome = client.get_filename() == WELCOME
        if not save and not is_welcome:
            self.save_notebook(client)
        if not is_welcome:
            client.shutdown_kernel()
        client.close()

        # Delete notebook file if it is in temporary directory
        filename = client.get_filename()
        if filename.startswith(get_temp_dir()):
            try:
                os.remove(filename)
            except EnvironmentError:
                pass

        # Note: notebook index may have changed after closing related widgets
        self.tabwidget.removeTab(self.tabwidget.indexOf(client))
        self.clients.remove(client)

        self.create_welcome_client()

    def create_welcome_client(self):
        """Create a welcome client with some instructions."""
        if self.tabwidget.count() == 0:
            welcome = open(WELCOME).read()
            client = NotebookClient(self, WELCOME, ini_message=welcome)
            self.add_tab(client)
            return client

    def save_notebook(self, client):
        """
        Save notebook corresponding to given client.

        If the notebook is newly created and not empty, then ask the user for
        a new filename and save under that name.

        This function is called when the user closes a tab.
        """
        client.save()

        # Check filename to find out whether notebook is newly created
        path = client.get_filename()
        dirname, basename = osp.split(path)
        if dirname != NOTEBOOK_TMPDIR or not basename.startswith('untitled'):
            return

        # Read file to see whether notebook is empty
        wait_save = QEventLoop()
        QTimer.singleShot(1000, wait_save.quit)
        wait_save.exec_()
        nb_contents = nbformat.read(path, as_version=4)
        if (len(nb_contents['cells']) == 0
                or len(nb_contents['cells'][0]['source']) == 0):
            return

        # Ask user to save notebook with new filename
        buttons = QMessageBox.Yes | QMessageBox.No
        text = _("<b>{0}</b> has been modified.<br>"
                 "Do you want to save changes?").format(basename)
        answer = QMessageBox.question(
            self, self.get_plugin_title(), text, buttons)
        if answer == QMessageBox.Yes:
            self.save_as(close=True)

    def save_as(self, name=None, close=False):
        """Save notebook as."""
        current_client = self.get_current_client()
        current_client.save()
        original_path = current_client.get_filename()
        if not name:
            original_name = osp.basename(original_path)
        else:
            original_name = name
        filename, _selfilter = getsavefilename(self, _("Save notebook"),
                                               original_name, FILES_FILTER)
        if filename:
            try:
                nb_contents = nbformat.read(original_path, as_version=4)
            except EnvironmentError as error:
                txt = (_("Error while reading {}<p>{}")
                       .format(original_path, str(error)))
                QMessageBox.critical(self, _("File Error"), txt)
                return
            try:
                nbformat.write(nb_contents, filename)
            except EnvironmentError as error:
                txt = (_("Error while writing {}<p>{}")
                       .format(filename, str(error)))
                QMessageBox.critical(self, _("File Error"), txt)
                return
            if not close:
                self.close_client(save=True)
            self.create_new_client(filename=filename)

    def open_notebook(self, filenames=None):
        """Open a notebook from file."""
        if not filenames:
            filenames, _selfilter = getopenfilenames(self, _("Open notebook"),
                                                     '', FILES_FILTER)
        if filenames:
            for filename in filenames:
                self.create_new_client(filename=filename)

    def open_console(self, client=None):
        """Open an IPython console for the given client or the current one."""
        if not client:
            client = self.get_current_client()
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

    # ------ Public API (for tabs) --------------------------------------------
    def add_tab(self, widget):
        """Add tab."""
        self.clients.append(widget)
        index = self.tabwidget.addTab(widget, widget.get_short_name())
        self.tabwidget.setCurrentIndex(index)
        self.tabwidget.setTabToolTip(index, widget.get_filename())
        if self.dockwidget:
            self.switch_to_plugin()
        self.activateWindow()

    def move_tab(self, index_from, index_to):
        """Move tab."""
        client = self.clients.pop(index_from)
        self.clients.insert(index_to, client)

    # ------ Public API (for FileSwitcher) ------------------------------------
    def handle_switcher_modes(self, mode):
        """
        Populate switcher with opened notebooks.

        List the file names of the opened notebooks with their directories in
        the switcher. Only handle file mode, where `mode` is empty string.
        """
        if mode != '':
            return

        paths = [client.get_filename() for client in self.clients]
        is_unsaved = [False for client in self.clients]
        short_paths = shorten_paths(paths, is_unsaved)
        icon = QIcon(os.path.join(PACKAGE_PATH, 'images', 'icon.svg'))
        section = self.get_plugin_title()

        for path, short_path, client in zip(paths, short_paths, self.clients):
            title = osp.basename(path)
            description = osp.dirname(path)
            if len(path) > 75:
                description = short_path
            is_last_item = (client == self.clients[-1])
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
        index = self.clients.index(client)
        self.tabwidget.setCurrentIndex(index)
        self.switch_to_plugin()
        self.switcher.hide()
