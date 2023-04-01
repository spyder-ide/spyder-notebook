# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for serverinfo.py."""

# Third party imports
import pytest

# Local imports
from spyder_notebook.utils.servermanager import ServerProcess, ServerState
from spyder_notebook.widgets.serverinfo import ServerInfoDialog


class FakeProcess:
    """Fake for ServerProcess class."""

    def __init__(self, pid):
        self.pid = pid

    def processId(self):
        """Member function which needs to be faked."""
        return self.pid


@pytest.fixture
def dialog(qtbot):
    """Construct and return dialog window for testing."""
    servers = [ServerProcess(FakeProcess(42), '/my/home/dir',
                             interpreter='/ham/interpreter',
                             info_file='info1.json',
                             state=ServerState.RUNNING,
                             output='Nicely humming along...\n'),
               ServerProcess(FakeProcess(404), '/some/other/dir',
                             interpreter='/spam/interpreter',
                             info_file='info2.json',
                             state=ServerState.FINISHED,
                             output='Terminated for some reason...\n')]
    res = ServerInfoDialog(servers)
    qtbot.addWidget(res)
    return res


def test_dialog_on_initialization(dialog):
    """Test that dialog's data is filled correctly after initialization."""
    assert dialog.process_combo.count() == 2
    assert dialog.process_combo.currentIndex() == 0
    assert dialog.process_combo.currentText() == '42'
    assert dialog.process_combo.itemText(1) == '404'
    assert dialog.state_lineedit.text() == 'Running'
    assert dialog.dir_lineedit.text() == '/my/home/dir'
    assert dialog.interpreter_lineedit.text() == '/ham/interpreter'
    assert dialog.log_textedit.toPlainText() == 'Nicely humming along...\n'


def test_dialog_change_process(dialog):
    """Test that dialog's data changes when user select another process."""
    dialog.process_combo.setCurrentIndex(1)

    assert dialog.process_combo.count() == 2
    assert dialog.process_combo.currentIndex() == 1
    assert dialog.process_combo.currentText() == '404'
    assert dialog.state_lineedit.text() == 'Finished'
    assert dialog.dir_lineedit.text() == '/some/other/dir'
    assert dialog.interpreter_lineedit.text() == '/spam/interpreter'
    assert (dialog.log_textedit.toPlainText()
            == 'Terminated for some reason...\n')
