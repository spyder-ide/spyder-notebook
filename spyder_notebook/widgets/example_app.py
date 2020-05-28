# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""
Simple application for working with notebooks.

This is a stand-alone application showing how spyder_notebook can be used
outside Spyder. It is mainly meant for development and testing purposes,
but it can also serve as an example.
"""

# Standard library imports
import sys

# Qt import
from qtpy.QtCore import QCoreApplication, Qt
from qtpy.QtQuick import QQuickWindow, QSGRendererInterface
from qtpy.QtWidgets import QApplication, QMainWindow

# Plugin imports
from spyder_notebook.widgets.notebooktabwidget import NotebookTabWidget


def use_software_rendering():
    """
    Instruct Qt to use software rendering.

    This is necessary for some buggy graphics drivers (e.g. nvidia).
    This function should be run before the QApplication is created.
    """
    QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)
    QQuickWindow.setSceneGraphBackend(QSGRendererInterface.Software)


class NotebookAppMainWindow(QMainWindow):
    """Main window for stand-alone notebook application."""

    def __init__(self):
        super().__init__()
        widget = NotebookTabWidget(self, None, None, None)
        widget.maybe_create_welcome_client()
        self.setCentralWidget(widget)


if __name__ == '__main__':
    use_software_rendering()
    app = QApplication([])
    window = NotebookAppMainWindow()
    window.show()
    sys.exit(app.exec_())
