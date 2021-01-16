# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""ServerInfoDialog, a dialog window showing info about notebook servers."""


# Standard library imports
import sys

# Qt imports
from qtpy.QtWidgets import (
    QApplication, QComboBox, QDialogButtonBox, QFormLayout, QLineEdit,
    QPushButton, QTextEdit, QVBoxLayout)

# Spyder imports
from spyder.plugins.variableexplorer.widgets.basedialog import BaseDialog

# Local imports
from spyder_notebook.utils.localization import _
from spyder_notebook.utils.servermanager import ServerProcess, ServerState


# Text description of the different server states
SERVER_STATE_DESCRIPTIONS = {
    ServerState.STARTING:  _('Starting up'),
    ServerState.RUNNING:   _('Running'),
    ServerState.FINISHED:  _('Finished'),
    ServerState.ERROR:     _('Error'),
    ServerState.TIMED_OUT: _('Timed out')}


class ServerInfoDialog(BaseDialog):
    """Dialog window showing information about notebook servers."""

    def __init__(self, server_info, parent=None):
        """
        Construct a RecoveryDialog.

        Parameters
        ----------
        servers : list of ServerProcess
            Information to be displayed. This parameter is read only.
        parent : QWidget, optional
            Parent of the dialog window. The default is None.
        """
        super().__init__(parent)
        self.servers = server_info

        self.setWindowTitle(_('Notebook server info'))

        self.layout = QVBoxLayout(self)
        self.formlayout = QFormLayout()
        self.layout.addLayout(self.formlayout)

        self.process_combo = QComboBox(self)
        self.process_combo.currentIndexChanged.connect(self.select_process)
        self.formlayout.addRow(_('Process ID:'), self.process_combo)

        self.dir_lineedit = QLineEdit(self)
        self.dir_lineedit.setReadOnly(True)
        self.formlayout.addRow(_('Notebook dir:'), self.dir_lineedit)

        self.interpreter_lineedit = QLineEdit(self)
        self.interpreter_lineedit.setReadOnly(True)
        self.formlayout.addRow(_('Python interpreter:'),
                               self.interpreter_lineedit)

        self.state_lineedit = QLineEdit(self)
        self.state_lineedit.setReadOnly(True)
        self.formlayout.addRow(_('State:'), self.state_lineedit)

        self.log_textedit = QTextEdit(self)
        self.log_textedit.setReadOnly(True)
        self.layout.addWidget(self.log_textedit)

        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok, self)
        self.buttonbox.accepted.connect(self.accept)
        self.refresh_button = QPushButton(_('Refresh'), self)
        self.refresh_button.clicked.connect(self.refresh_data)
        self.buttonbox.addButton(
            self.refresh_button, QDialogButtonBox.ActionRole)
        self.layout.addWidget(self.buttonbox)

        self.refresh_data()

    def refresh_data(self):
        self.process_combo.clear()
        for server in self.servers:
            self.process_combo.addItem(str(server.process.processId()))
        self.select_process(0)

    def select_process(self, index):
        self.dir_lineedit.setText(self.servers[index].notebook_dir)
        self.interpreter_lineedit.setText(self.servers[index].interpreter)
        self.state_lineedit.setText(
            SERVER_STATE_DESCRIPTIONS[self.servers[index].state])
        self.log_textedit.setPlainText(self.servers[index].output)


def test():  # pragma: no cover
    """Display dialog for manual testing."""
    class FakeProcess:
        def __init__(self, pid):
            self.pid = pid

        def processId(self):
            return self.pid

    servers = [ServerProcess(FakeProcess(42), '/my/home/dir',
                             '/ham/interpreter',
                             state=ServerState.RUNNING,
                             output='Nicely humming along...\n'),
               ServerProcess(FakeProcess(404), '/some/other/dir',
                             '/spam/interpreter',
                             state=ServerState.FINISHED,
                             output='Terminated for some reason...\n')]

    app = QApplication(sys.argv)
    dialog = ServerInfoDialog(servers)
    dialog.show()
    sys.exit(app.exec_())


if __name__ == "__main__":  # pragma: no cover
    test()
