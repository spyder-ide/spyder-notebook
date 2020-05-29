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
from qtpy.QtWidgets import QAction, QApplication, QMainWindow

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
        self.tabwidget = NotebookTabWidget(self, None, None, None)
        self.tabwidget.maybe_create_welcome_client()
        self.setCentralWidget(self.tabwidget)
        self._setup_menu()

    def _setup_menu(self):
        file_menu = self.menuBar().addMenu('File')

        new_action = QAction('New Notebook', self)
        new_action.triggered.connect(self.tabwidget.create_new_client)
        file_menu.addAction(new_action)

        open_action = QAction('Open Notebook...', self)
        open_action.triggered.connect(self.tabwidget.open_notebook)
        file_menu.addAction(open_action)

        save_action = QAction('Save Notebook', self)
        save_action.triggered.connect(
            lambda checked: self.tabwidget.save_notebook(
                self.tabwidget.currentWidget()))
        file_menu.addAction(save_action)

        saveas_action = QAction('Save As...', self)
        saveas_action.triggered.connect(self.tabwidget.save_as)
        file_menu.addAction(saveas_action)

        close_action = QAction('Close Notebook', self)
        close_action.triggered.connect(
            lambda checked: self.tabwidget.close_client(
                self.tabwidget.currentIndex()))
        file_menu.addAction(close_action)


if __name__ == '__main__':
    use_software_rendering()
    app = QApplication([])
    window = NotebookAppMainWindow()
    window.show()
    sys.exit(app.exec_())
