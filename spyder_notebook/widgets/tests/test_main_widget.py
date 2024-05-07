# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for NotebookMainWidget"""

# Standard library imports
import os
import os.path as osp
import shutil
import sys
from unittest.mock import MagicMock

# Third-party library imports
from flaky import flaky
import pytest
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QFileDialog, QApplication, QLineEdit

# Local imports
from spyder_notebook.tests.test_plugin import (
    is_kernel_up, prompt_present, text_present)
from spyder_notebook.widgets.main_widget import NotebookMainWidget

# =============================================================================
# Constants
# =============================================================================
NOTEBOOK_UP = 40000
INTERACTION_CLICK = 100
LOCATION = osp.realpath(osp.join(os.getcwd(), osp.dirname(__file__)))


# =============================================================================
# Utility functions
# =============================================================================
def manage_save_dialog(qtbot, fname, directory=LOCATION):
    """
    Manage the QFileDialog when saving.

    You can use this with QTimer to manage the QFileDialog.
    Before calling anything that may show a QFileDialog for save call:
    QTimer.singleShot(1000, lambda: manage_save_dialog(qtbot))
    """
    top_level_widgets = QApplication.topLevelWidgets()
    for w in top_level_widgets:
        if isinstance(w, QFileDialog):
            if directory is not None:
                w.setDirectory(directory)
            input_field = w.findChildren(QLineEdit)[0]
            input_field.setText(fname)
            qtbot.keyClick(w, Qt.Key_Enter)


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture
def main_widget(qtbot):
    """Set up a NotebookMainWidget, with no tabs."""
    mock_plugin = MagicMock()
    mock_plugin.CONF_SECTION = 'mock conf section'

    main_widget = NotebookMainWidget('testwidget', mock_plugin, None)
    main_widget._setup()
    main_widget.setup()
    main_widget.show()  # Prompt only appears if widget is displayed
    
    yield main_widget

    main_widget.close()


# =============================================================================
# Tests
# =============================================================================
@flaky(max_runs=3)
def test_new_notebook(main_widget, qtbot):
    """Test that a new client is really a notebook."""
    # Create new notebook tab and check that there is a prompt
    main_widget.create_new_client()
    nbwidget = main_widget.tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)


@flaky(max_runs=3)
@pytest.mark.skipif(sys.platform == 'darwin', reason='Prompt never comes up')
def test_open_notebook_in_non_ascii_dir(main_widget, qtbot, tmpdir):
    """Test that a notebook can be opened from a non-ascii directory."""
    # Copy the test file to non-ascii directory
    test_notebook = osp.join(LOCATION, 'test.ipynb')
    test_notebook_non_ascii = osp.join(str(tmpdir), u'äöüß', 'test.ipynb')
    os.mkdir(os.path.join(str(tmpdir), u'äöüß'))
    shutil.copyfile(test_notebook, test_notebook_non_ascii)

    # Open the test notebook and wait for prompt
    main_widget.open_notebook(filenames=[test_notebook_non_ascii])
    client = main_widget.tabwidget.currentWidget()
    nbwidget = client.notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "Test" in it
    # and the client has the correct name
    qtbot.waitUntil(lambda: text_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)
    assert text_present(nbwidget, qtbot)
    assert client.get_short_name() == "test"


@flaky(max_runs=3)
@pytest.mark.skipif(not sys.platform.startswith('linux'),
                    reason='Test hangs on CI on Windows and MacOS')
def test_save_notebook(main_widget, qtbot, tmpdir):
    """Test that a notebook can be saved."""
    # Create new notebook tab and wait for prompt
    main_widget.create_new_client()
    nbwidget = main_widget.tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Writes: a = "test"
    qtbot.keyClick(nbwidget, Qt.Key_A, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_Space, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_Equal, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_Space, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_QuoteDbl, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_T, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_E, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_S, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_T, delay=INTERACTION_CLICK)
    qtbot.keyClick(nbwidget, Qt.Key_QuoteDbl, delay=INTERACTION_CLICK)

    # Save the notebook
    name = osp.join(str(tmpdir), 'save.ipynb')
    QTimer.singleShot(1000, lambda: manage_save_dialog(qtbot, fname=name))
    main_widget.save_as()

    # Wait for prompt
    client = main_widget.tabwidget.currentWidget()
    nbwidget = client.notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Assert that the In prompt has "test" in it
    # and the client has the correct name
    qtbot.waitUntil(lambda: text_present(nbwidget, qtbot, text="test"),
                    timeout=NOTEBOOK_UP)
    assert text_present(nbwidget, qtbot, text="test")
    assert client.get_short_name() == "save"


@flaky(max_runs=3)
@pytest.mark.skipif(os.name == 'nt',
                    reason='Test hangs often on CI on Windows')
def test_save_notebook_as_with_error(main_widget, mocker, qtbot, tmpdir):
    """Test that errors are handled in save_as()."""
    # Create new notebook tab and wait for prompt
    main_widget.create_new_client()
    nbwidget = main_widget.tabwidget.currentWidget().notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Set up mocks
    name = osp.join(str(tmpdir), 'save.ipynb')
    mocker.patch('spyder_notebook.widgets.notebooktabwidget.getsavefilename',
                 return_value=(name, 'ignored'))
    mocker.patch('spyder_notebook.widgets.notebooktabwidget.nbformat.write',
                 side_effect=PermissionError)
    mock_critical = mocker.patch('spyder_notebook.widgets.notebooktabwidget'
                                 '.QMessageBox.critical')

    # Save the notebook
    main_widget.save_as()

    # Assert that message box is displayed (reporting error raised by write)
    assert mock_critical.called


@flaky(max_runs=5)
def test_shutdown_notebook_kernel(main_widget, qtbot):
    """Test that kernel is shut down when closing a notebook."""
    # Create new notebook tab and wait for prompt
    main_widget.create_new_client()
    client = main_widget.tabwidget.currentWidget()
    nbwidget = client.notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Get kernel id for the client
    qtbot.waitUntil(lambda: client.get_kernel_id() is not None,
                    timeout=NOTEBOOK_UP)
    kernel_id = client.get_kernel_id()
    
    # Assert that kernel is up
    sessions_url = client.get_session_url()
    assert is_kernel_up(kernel_id, sessions_url)

    # Close the current client
    main_widget.tabwidget.close_client()

    # Assert that the kernel is down for the closed client
    assert not is_kernel_up(kernel_id, sessions_url)


def test_file_in_temp_dir_deleted_after_notebook_closed(main_widget, qtbot):
    """Test that notebook file in temporary directory is deleted after the
    notebook is closed."""
    # Create new notebook tab and wait for prompt
    main_widget.create_new_client()
    client = main_widget.tabwidget.currentWidget()
    nbwidget = client.notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    # Get file name
    filename = client.get_filename()

    # Close the current client
    main_widget.tabwidget.close_client()

    # Assert file is deleted
    assert not osp.exists(filename)


@flaky(max_runs=3)
def test_close_nonexisting_notebook(main_widget, qtbot, tmpdir):
    """Test that we can close a tab if the notebook file does not exist.
    Regression test for spyder-ide/spyder-notebook#187."""
    # Set up tab with non-existing notebook
    test_notebook_original = osp.join(LOCATION, 'test.ipynb')
    test_notebook = osp.join(str(tmpdir), 'test.ipynb')
    shutil.copyfile(test_notebook_original, test_notebook)
    main_widget.open_notebook(filenames=[test_notebook])

    # Wait for prompt
    client = main_widget.tabwidget.currentWidget()
    nbwidget = client.notebookwidget
    qtbot.waitUntil(lambda: prompt_present(nbwidget, qtbot),
                    timeout=NOTEBOOK_UP)

    os.remove(test_notebook)

    # Close tab
    main_widget.tabwidget.close_client()

    # Assert tab is closed (without raising an exception)
    for client_index in range(main_widget.tabwidget.count()):
        assert client != main_widget.tabwidget.widget(client_index)
