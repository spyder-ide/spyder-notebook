# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Qt widgets for the notebook."""

# Standard library imports
from string import Template
import os
import os.path as osp
import sys

# Third party imports
from notebook.utils import url_escape, url_path_join
from qtpy.QtCore import QUrl
from qtpy.QtWebEngineWidgets import (WEBENGINE, QWebEnginePage,
                                     QWebEngineSettings)
from qtpy.QtWidgets import QMenu, QVBoxLayout, QWidget
from spyder.config.base import _, get_image_path, get_module_source_path
from spyder.py3compat import is_text_string
from spyder.utils import sourcecode
from spyder.utils.qthelpers import add_actions
from spyder.widgets.findreplace import FindReplace

# Local relative imports
from ..widgets.dom import DOMWidget

#-----------------------------------------------------------------------------
# Templates
#-----------------------------------------------------------------------------
# Using the same css file from the Help plugin for now. Maybe
# later it'll be a good idea to create a new one.
UTILS_PATH = get_module_source_path('spyder', 'utils')
CSS_PATH = osp.join(UTILS_PATH, 'help', 'static', 'css')
TEMPLATES_PATH = osp.join(UTILS_PATH, 'ipython', 'templates')

BLANK = open(osp.join(TEMPLATES_PATH, 'blank.html')).read()
LOADING = open(osp.join(TEMPLATES_PATH, 'loading.html')).read()
KERNEL_ERROR = open(osp.join(TEMPLATES_PATH, 'kernel_error.html')).read()


#-----------------------------------------------------------------------------
# Widgets
#-----------------------------------------------------------------------------
class NotebookWidget(DOMWidget):
    """WebView widget for notebooks."""

    def contextMenuEvent(self, event):
        """Don't show some actions which have no meaning for the IPython
        notebook."""
        menu = QMenu(self)
        actions = [self.pageAction(QWebEnginePage.SelectAll),
                   self.pageAction(QWebEnginePage.Copy), None,
                   self.zoom_in_action, self.zoom_out_action]
        if not WEBENGINE:
            settings = self.page().settings()
            settings.setAttribute(QWebEngineSettings.DeveloperExtrasEnabled, True)
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

        message = _("An error ocurred while starting the kernel")
        kernel_error_template = Template(KERNEL_ERROR)
        page = kernel_error_template.substitute(css_path=CSS_PATH,
                                                message=message,
                                                error=error)
        self.setHtml(page)

    def show_loading_page(self):
        """Show a loading animation while the kernel is starting"""
        loading_template = Template(LOADING)
        loading_img = get_image_path('loading_sprites.png')
        if os.name == 'nt':
            loading_img = loading_img.replace('\\', '/')
        message = _("Connecting to kernel...")
        page = loading_template.substitute(css_path=CSS_PATH,
                                           loading_img=loading_img,
                                           message=message)
        self.setHtml(page)



class NotebookClient(QWidget):
    """
    Notebook client for Spyder.

    This is a widget composed of a NotebookWidget and a find dialog to
    render notebooks.
    """
    def __init__(self, plugin, name):
        super(NotebookClient, self).__init__(plugin)

        self.name = name

        self.file_url = None
        self.server_url = None
        self.path = None

        self.notebookwidget = NotebookWidget(self)
        self.notebookwidget.show_loading_page()

        self.find_widget = FindReplace(self)
        self.find_widget.set_editor(self.notebookwidget)
        self.find_widget.hide()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.notebookwidget)
        layout.addWidget(self.find_widget)
        self.setLayout(layout)

    def register(self, server_info):
        """Register attributes that can be computed with the server info."""
        # Path relative to the server directory
        self.path = os.path.relpath(self.name,
                                    start=server_info['notebook_dir'])

        # Full url used to render the notebook as a web page
        self.file_url = url_path_join(server_info['url'],
                                      'notebooks',
                                      url_escape(self.path.replace('\\','/')))

        # Server url to send requests to
        self.server_url = server_info['url']

    def go_to(self, url_or_text):
        """Go to page *address*"""
        if is_text_string(url_or_text):
            url = QUrl(url_or_text)
        else:
            url = url_or_text
        self.notebookwidget.load(url)

    def load_notebook(self):
        self.go_to(self.file_url)

    def get_name(self):
        return self.name

    def get_short_name(self):
        """Get a short name for the notebook."""
        sname = osp.basename(self.name)
        if len(sname) > 15:
            sname = sname[:15]
        return sname

    def save(self):
        """Save current notebook."""
        self.notebookwidget.click('#save-notbook button')


#-----------------------------------------------------------------------------
# Tests
#-----------------------------------------------------------------------------
def main():
    from spyder.utils.qthelpers import qapplication
    app = qapplication()
    widget = NotebookClient(plugin=None, name='')
    widget.show()
    widget.set_url('http://google.com')
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
