# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""Qt widgets for the notebook."""

import os
import os.path as osp
import json
from string import Template
import sys

# Qt imports
from qtpy.QtCore import QUrl, Qt
from qtpy.QtGui import QFontMetrics, QFont
from qtpy.QtWebEngineWidgets import (QWebEnginePage, QWebEngineSettings,
                                     WEBENGINE)
from qtpy.QtWidgets import QMenu, QVBoxLayout, QWidget, QMessageBox

# Notebook imports
from notebook.utils import url_path_join, url_escape

# Third-party imports
import requests

# Spyder imports
from spyder.config.base import _, get_image_path, get_module_source_path
from spyder.py3compat import is_text_string
from spyder.utils.qthelpers import add_actions
from spyder.utils import sourcecode
from spyder.widgets.findreplace import FindReplace

# Local imports
from ..widgets.dom import DOMWidget

# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------
# Using the same css file from the Help plugin for now. Maybe
# later it'll be a good idea to create a new one.
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError  # Python 2

PLUGINS_PATH = get_module_source_path('spyder', 'plugins')
CSS_PATH = osp.join(PLUGINS_PATH, 'help', 'utils', 'static', 'css')
TEMPLATES_PATH = osp.join(
        PLUGINS_PATH, 'ipythonconsole', 'assets', 'templates')
open(osp.join(TEMPLATES_PATH, 'blank.html'))

BLANK = open(osp.join(TEMPLATES_PATH, 'blank.html')).read()
LOADING = open(osp.join(TEMPLATES_PATH, 'loading.html')).read()
KERNEL_ERROR = open(osp.join(TEMPLATES_PATH, 'kernel_error.html')).read()


# -----------------------------------------------------------------------------
# Widgets
# -----------------------------------------------------------------------------
class NotebookWidget(DOMWidget):
    """WebView widget for notebooks."""

    def contextMenuEvent(self, event):
        """Don't show some actions which have no meaning for the notebook."""
        menu = QMenu(self)
        plugin_actions = self.parent().plugin_actions
        actions = plugin_actions + [None,
                                    self.pageAction(QWebEnginePage.SelectAll),
                                    self.pageAction(QWebEnginePage.Copy), None,
                                    self.zoom_in_action, self.zoom_out_action]
        if not WEBENGINE:
            settings = self.page().settings()
            settings.setAttribute(QWebEngineSettings.DeveloperExtrasEnabled,
                                  True)
            actions += [None, self.pageAction(QWebEnginePage.InspectElement)]
        add_actions(menu, actions)
        menu.popup(event.globalPos())
        event.accept()

    def show_blank(self):
        """Show a blank page."""
        self.setHtml(BLANK)

    def show_kernel_error(self, error):
        """Show kernel initialization errors."""
        # Remove unneeded blank lines at the beginning
        eol = sourcecode.get_eol_chars(error)
        if eol:
            error = error.replace(eol, '<br>')
        # Don't break lines in hyphens
        # From http://stackoverflow.com/q/7691569/438386
        error = error.replace('-', '&#8209')

        message = _("An error occurred while starting the kernel")
        kernel_error_template = Template(KERNEL_ERROR)
        page = kernel_error_template.substitute(css_path=CSS_PATH,
                                                message=message,
                                                error=error)
        self.setHtml(page)

    def show_loading_page(self):
        """Show a loading animation while the kernel is starting."""
        loading_template = Template(LOADING)
        loading_img = get_image_path('loading_sprites.png')
        if os.name == 'nt':
            loading_img = loading_img.replace('\\', '/')
        message = _("Connecting to kernel...")
        page = loading_template.substitute(css_path=CSS_PATH,
                                           loading_img=loading_img,
                                           message=message)
        self.setHtml(page)

    def show_message(self, page):
        """Show a message page with the given .html file."""
        self.setHtml(page)


class NotebookClient(QWidget):
    """
    Notebook client for Spyder.

    This is a widget composed of a NotebookWidget and a find dialog to
    render notebooks.
    """

    def __init__(self, plugin, filename, ini_message=None):
        """Constructor."""
        super(NotebookClient, self).__init__(plugin)

        if os.name == 'nt':
            filename = filename.replace('/', '\\')
        self.filename = filename

        self.file_url = None
        self.server_url = None
        self.path = None

        self.plugin_actions = plugin.get_plugin_actions()
        self.notebookwidget = NotebookWidget(self)
        if WEBENGINE:
            self.notebookwidget.loadFinished.connect(self.hide_header)
        else:
            self.notebookwidget.selectionChanged.connect(self.hide_header)
        self.notebookwidget.urlChanged.connect(self.hide_header)
        if ini_message:
            self.notebookwidget.show_message(ini_message)
        else:
            self.notebookwidget.show_blank()

        self.find_widget = FindReplace(self)
        self.find_widget.set_editor(self.notebookwidget)
        self.find_widget.hide()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.notebookwidget)
        layout.addWidget(self.find_widget)
        self.setLayout(layout)

    def add_token(self, url):
        """Add notebook token to a given url."""
        token_url = url + '?token={}'.format(self.token)
        return token_url

    def register(self, server_info):
        """Register attributes that can be computed with the server info."""
        # Path relative to the server directory
        self.path = os.path.relpath(self.filename,
                                    start=server_info['notebook_dir'])

        # Replace backslashes on Windows
        if os.name == 'nt':
            self.path = self.path.replace('\\', '/')

        # Server url to send requests to
        self.server_url = server_info['url']

        # Server token
        self.token = server_info['token']

        url = url_path_join(self.server_url, 'notebooks',
                            url_escape(self.path))

        # Set file url to load this notebook
        self.file_url = self.add_token(url)

    def go_to(self, url_or_text):
        """Go to page utl."""
        if is_text_string(url_or_text):
            url = QUrl(url_or_text)
        else:
            url = url_or_text
        self.notebookwidget.load(url)

    def load_notebook(self):
        """Load the associated notebook."""
        self.go_to(self.file_url)

    def hide_header(self):
        """Hide the header of the notebook."""
        self.notebookwidget.set_class_value("#header-container", "hidden")

    def get_filename(self):
        """Get notebook's filename."""
        return self.filename

    def get_short_name(self):
        """Get a short name for the notebook."""
        sname = osp.splitext(osp.basename(self.filename))[0]
        if len(sname) > 20:
            fm = QFontMetrics(QFont())
            sname = fm.elidedText(sname, Qt.ElideRight, 110)
        return sname

    def save(self):
        """Save current notebook."""
        self.notebookwidget.click("#save-notbook button")

    def get_session_url(self):
        """Get the kernel sessions url of the client."""
        return self.add_token(url_path_join(self.server_url, 'api/sessions'))

    def get_kernel_id(self):
        """
        Get the kernel id of the client.

        Return a str with the kernel id or None. On error, display a dialog
        box and return None.
        """
        sessions_url = self.get_session_url()
        try:
            sessions_response = requests.get(sessions_url)
        except requests.exceptions.RequestException as exception:
            msg = _('Spyder could not get a list of sessions '
                    'from the Jupyter Notebook server. '
                    'Message: {}').format(exception)
            QMessageBox.warning(self, _('Server error'), msg)
            return None

        sessions = json.loads(sessions_response.content.decode())
        if sessions_response.status_code != requests.codes.ok:
            msg = _('Spyder could not get a list of sessions '
                    'from the Jupyter Notebook server. '
                    'Message: {}').format(sessions.get('message'))
            QMessageBox.warning(self, _('Server error'), msg)
            return None

        if os.name == 'nt':
            path = self.path.replace('\\', '/')
        else:
            path = self.path

        for session in sessions:
            notebook_path = session.get('notebook', {}).get('path')
            if notebook_path is not None and notebook_path == path:
                kernel_id = session['kernel']['id']
                return kernel_id

    def shutdown_kernel(self):
        """Shutdown the kernel of the client."""
        kernel_id = self.get_kernel_id()

        if kernel_id:
            delete_url = self.add_token(url_path_join(self.server_url,
                                                      'api/kernels/',
                                                      kernel_id))
            delete_req = requests.delete(delete_url)
            if delete_req.status_code != 204:
                QMessageBox.warning(
                    self,
                    _("Server error"),
                    _("The Jupyter Notebook server "
                      "failed to shutdown the kernel "
                      "associated with this notebook. "
                      "If you want to shut it down, "
                      "you'll have to close Spyder."))


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
def main():
    """Simple test."""
    from spyder.utils.qthelpers import qapplication
    app = qapplication()
    widget = NotebookClient(plugin=None, name='')
    widget.show()
    widget.set_url('http://google.com')
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
