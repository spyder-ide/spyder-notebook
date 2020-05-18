/**
 * Set up keyboard shortcuts & commands for notebook
 */
import { CommandRegistry } from '@phosphor/commands';
import { Menu, MenuBar } from '@phosphor/widgets';
import { CompletionHandler } from '@jupyterlab/completer';
import { NotebookPanel, NotebookActions } from '@jupyterlab/notebook';
import {
  SearchInstance,
  NotebookSearchProvider
} from '@jupyterlab/documentsearch';

/**
 * The map of command ids used by the notebook.
 */
const cmdIds = {
  invoke: 'completer:invoke',
  select: 'completer:select',
  invokeNotebook: 'completer:invoke-notebook',
  selectNotebook: 'completer:select-notebook',
  startSearch: 'documentsearch:start-search',
  findNext: 'documentsearch:find-next',
  findPrevious: 'documentsearch:find-previous',
  save: 'notebook:save',
  interrupt: 'notebook:interrupt-kernel',
  restart: 'notebook:restart-kernel',
  switchKernel: 'notebook:switch-kernel',
  undo: 'notebook-cells:undo',
  redo: 'notebook-cells:redo',
  cut: 'notebook:cut-cell',
  copy: 'notebook:copy-cell',
  pasteAbove: 'notebook:paste-cell-above',
  pasteBelow: 'notebook:paste-cell-below',
  pasteAndReplace: 'notebook:paste-and-replace-cell',
  deleteCell: 'notebook:delete-cell',
  selectAll: 'notebook:select-all',
  deselectAll: 'notebook:deselect-all',
  moveUp: 'notebook:move-cell-up',
  moveDown: 'notebook:move-cell-down',
  split: 'notebook:split-cell-at-cursor',
  merge: 'notebook:merge-cells',
  clearOutputs: 'notebook:clear-cell-output',
  clearAllOutputs: 'notebook:clear-all-cell-outputs',
  runAndAdvance: 'notebook-cells:run-and-advance',
  run: 'notebook:run-cell',
  runAndInsert: 'notebook-cells:run-cell-and-insert-below',
  runAllAbove: 'notebook-cells:run-all-above',
  runAllBelow: 'notebook-cells:run-all-below',
  renderAllMarkdown: 'notebook-cells:render-all-markdown',
  runAll: 'notebook-cells:run-all-cells',
  restartRunAll: 'notebook:restart-run-all',
  selectAbove: 'notebook-cells:select-above',
  selectBelow: 'notebook-cells:select-below',
  extendAbove: 'notebook-cells:extend-above',
  extendTop: 'notebook-cells:extend-top',
  extendBelow: 'notebook-cells:extend-below',
  extendBottom: 'notebook-cells:extend-bottom',
  editMode: 'notebook:edit-mode',
  commandMode: 'notebook:command-mode'
};

export const SetupCommands = (
  commands: CommandRegistry,
  menuBar: MenuBar,
  nbWidget: NotebookPanel,
  handler: CompletionHandler
) => {
  // Add commands.
  commands.addCommand(cmdIds.invoke, {
    label: 'Completer: Invoke',
    execute: () => handler.invoke()
  });
  commands.addCommand(cmdIds.select, {
    label: 'Completer: Select',
    execute: () => handler.completer.selectActive()
  });
  commands.addCommand(cmdIds.invokeNotebook, {
    label: 'Invoke Notebook',
    execute: () => {
      if (nbWidget.content.activeCell.model.type === 'code') {
        return commands.execute(cmdIds.invoke);
      }
    }
  });
  commands.addCommand(cmdIds.selectNotebook, {
    label: 'Select Notebook',
    execute: () => {
      if (nbWidget.content.activeCell.model.type === 'code') {
        return commands.execute(cmdIds.select);
      }
    }
  });
  commands.addCommand(cmdIds.save, {
    label: 'Save',
    execute: () => nbWidget.context.save()
  });

  let searchInstance: SearchInstance;
  commands.addCommand(cmdIds.startSearch, {
    label: 'Find...',
    execute: () => {
      if (searchInstance) {
        searchInstance.focusInput();
        return;
      }
      const provider = new NotebookSearchProvider();
      searchInstance = new SearchInstance(nbWidget, provider);
      searchInstance.disposed.connect(() => {
        searchInstance = undefined;
        // find next and previous are now not enabled
        commands.notifyCommandChanged();
      });
      // find next and previous are now enabled
      commands.notifyCommandChanged();
      searchInstance.focusInput();
    }
  });
  commands.addCommand(cmdIds.findNext, {
    label: 'Find Next',
    isEnabled: () => !!searchInstance,
    execute: async () => {
      if (!searchInstance) {
        return;
      }
      await searchInstance.provider.highlightNext();
      searchInstance.updateIndices();
    }
  });
  commands.addCommand(cmdIds.findPrevious, {
    label: 'Find Previous',
    isEnabled: () => !!searchInstance,
    execute: async () => {
      if (!searchInstance) {
        return;
      }
      await searchInstance.provider.highlightPrevious();
      searchInstance.updateIndices();
    }
  });
  commands.addCommand(cmdIds.interrupt, {
    label: 'Interrupt',
    execute: async () => {
      if (nbWidget.context.session.kernel) {
        await nbWidget.context.session.kernel.interrupt();
      }
    }
  });
  commands.addCommand(cmdIds.restart, {
    label: 'Restart Kernel',
    execute: () => nbWidget.context.session.restart()
  });
  commands.addCommand(cmdIds.switchKernel, {
    label: 'Switch Kernel',
    execute: () => nbWidget.context.session.selectKernel()
  });

  /**
   * Whether notebook has a single selected cell.
   */
  function isSingleSelected(): boolean {
    const content = nbWidget.content;
    const index = content.activeCellIndex;
    // If there are selections that are not the active cell,
    // this command is confusing, so disable it.
    for (let i = 0; i < content.widgets.length; ++i) {
      if (content.isSelected(content.widgets[i]) && i !== index) {
        return false;
      }
    }
    return true;
  }

  // Commands in Edit menu.
  commands.addCommand(cmdIds.undo, {
    label: 'Undo',
    execute: () => NotebookActions.undo(nbWidget.content)
  });

  commands.addCommand(cmdIds.redo, {
    label: 'Redo',
    execute: () => NotebookActions.redo(nbWidget.content)
  });

  commands.addCommand(cmdIds.cut, {
    label: 'Cut Cells',
    execute: () => NotebookActions.cut(nbWidget.content)
  });

  commands.addCommand(cmdIds.copy, {
    label: 'Copy Cells',
    execute: () => NotebookActions.copy(nbWidget.content)
  });

  commands.addCommand(cmdIds.pasteBelow, {
    label: 'Paste Cells Below',
    execute: () => NotebookActions.paste(nbWidget.content, 'below')
  });

  commands.addCommand(cmdIds.pasteAbove, {
    label: 'Paste Cells Above',
    execute: () => NotebookActions.paste(nbWidget.content, 'above')
  });

  commands.addCommand(cmdIds.pasteAndReplace, {
    label: 'Paste Cells and Replace',
    execute: () => NotebookActions.paste(nbWidget.content, 'replace')
  });

  commands.addCommand(cmdIds.deleteCell, {
    label: 'Delete Cells',
    execute: () => NotebookActions.deleteCells(nbWidget.content)
  });

  commands.addCommand(cmdIds.selectAll, {
    label: 'Select All Cells',
    execute: () => NotebookActions.selectAll(nbWidget.content)
  });

  commands.addCommand(cmdIds.deselectAll, {
    label: 'Deselect All Cells',
    execute: () => NotebookActions.deselectAll(nbWidget.content)
  });

  commands.addCommand(cmdIds.moveUp, {
    label: 'Move Cells Up',
    execute: () => NotebookActions.moveUp(nbWidget.content)
  });

  commands.addCommand(cmdIds.moveDown, {
    label: 'Move Cells Down',
    execute: () => NotebookActions.moveDown(nbWidget.content)
  });

  commands.addCommand(cmdIds.split, {
    label: 'Split Cell',
    execute: () => NotebookActions.splitCell(nbWidget.content)
  });

  commands.addCommand(cmdIds.merge, {
    label: 'Merge Selected Cells',
    execute: () => NotebookActions.mergeCells(nbWidget.content)
  });

  commands.addCommand(cmdIds.clearOutputs, {
    label: 'Clear Outputs',
    execute: () => NotebookActions.clearOutputs(nbWidget.content)
  });

  commands.addCommand(cmdIds.clearAllOutputs, {
    label: 'Clear All Outputs',
    execute: () => NotebookActions.clearAllOutputs(nbWidget.content)
  });

  // Commands in Run menu.
  commands.addCommand(cmdIds.runAndAdvance, {
    label: 'Run Selected Cells',
    execute: () => {
      return NotebookActions.runAndAdvance(
        nbWidget.content,
        nbWidget.context.session
      );
    }
  });

  commands.addCommand(cmdIds.run, {
    label: "Run Selected Cells and Don't Advance",
    execute: () => {
      return NotebookActions.run(
        nbWidget.content,
        nbWidget.context.session
      );
    }
  });

  commands.addCommand(cmdIds.runAndInsert, {
    label: 'Run Selected Cells and Insert Below',
    execute: () => {
      return NotebookActions.runAndInsert(
        nbWidget.content,
        nbWidget.context.session
      );
    }
  });

  commands.addCommand(cmdIds.runAllAbove, {
    label: 'Run All Above Selected Cell',
    execute: () => {
      return NotebookActions.runAllAbove(
        nbWidget.content,
        nbWidget.context.session
      );
    },
    isEnabled: () => {
      // Can't run above if there are multiple cells selected,
      // or if we are at the top of the notebook.
      return isSingleSelected() && nbWidget.content.activeCellIndex !== 0;
    }
  });

  commands.addCommand(cmdIds.runAllBelow, {
    label: 'Run Selected Cell and All Below',
    execute: () => {
      return NotebookActions.runAllBelow(
        nbWidget.content,
        nbWidget.context.session
      );
    },
    isEnabled: () => {
      // Can't run below if there are multiple cells selected,
      // or if we are at the bottom of the notebook.
      return (
        isSingleSelected() &&
        nbWidget.content.activeCellIndex !==
          nbWidget.content.widgets.length - 1
      );
    }
  });

  commands.addCommand(cmdIds.renderAllMarkdown, {
    label: 'Render All Markdown Cells',
    execute: () => {
      return NotebookActions.renderAllMarkdown(
        nbWidget.content,
        nbWidget.context.session
      );
    }
  });

  commands.addCommand(cmdIds.runAll, {
    label: 'Run All Cells',
    execute: () => {
      return NotebookActions.runAll(
        nbWidget.content,
        nbWidget.context.session
      );
    }
  });

  commands.addCommand(cmdIds.restartRunAll, {
    label: 'Restart Kernel and Run All Cells…',
    execute: () => {
      return nbWidget.session.restart().then(restarted => {
        if (restarted) {
          void NotebookActions.runAll(
            nbWidget.content,
            nbWidget.context.session
          );
        }
        return restarted;
      });
    }
  });

  commands.addCommand(cmdIds.editMode, {
    label: 'Edit Mode',
    execute: () => {
      nbWidget.content.mode = 'edit';
    }
  });
  commands.addCommand(cmdIds.commandMode, {
    label: 'Command Mode',
    execute: () => {
      nbWidget.content.mode = 'command';
    }
  });
  commands.addCommand(cmdIds.selectBelow, {
    label: 'Select Below',
    execute: () => NotebookActions.selectBelow(nbWidget.content)
  });
  commands.addCommand(cmdIds.selectAbove, {
    label: 'Select Above',
    execute: () => NotebookActions.selectAbove(nbWidget.content)
  });
  commands.addCommand(cmdIds.extendAbove, {
    label: 'Extend Above',
    execute: () => NotebookActions.extendSelectionAbove(nbWidget.content)
  });
  commands.addCommand(cmdIds.extendTop, {
    label: 'Extend to Top',
    execute: () => NotebookActions.extendSelectionAbove(nbWidget.content, true)
  });
  commands.addCommand(cmdIds.extendBelow, {
    label: 'Extend Below',
    execute: () => NotebookActions.extendSelectionBelow(nbWidget.content)
  });
  commands.addCommand(cmdIds.extendBottom, {
    label: 'Extend to Bottom',
    execute: () => NotebookActions.extendSelectionBelow(nbWidget.content, true)
  });

  let bindings = [
    {
      selector: '.jp-Notebook.jp-mod-editMode .jp-mod-completer-enabled',
      keys: ['Tab'],
      command: cmdIds.invokeNotebook
    },
    {
      selector: `.jp-mod-completer-active`,
      keys: ['Enter'],
      command: cmdIds.selectNotebook
    },
    {
      selector: '.jp-Notebook',
      keys: ['Shift Enter'],
      command: cmdIds.runAndAdvance
    },
    {
      selector: '.jp-Notebook',
      keys: ['Accel S'],
      command: cmdIds.save
    },
    {
      selector: '.jp-Notebook',
      keys: ['Accel F'],
      command: cmdIds.startSearch
    },
    {
      selector: '.jp-Notebook',
      keys: ['Accel G'],
      command: cmdIds.findNext
    },
    {
      selector: '.jp-Notebook',
      keys: ['Accel Shift G'],
      command: cmdIds.findPrevious
    },
    {
      selector: '.jp-Notebook.jp-mod-commandMode:focus',
      keys: ['I', 'I'],
      command: cmdIds.interrupt
    },
    {
      selector: '.jp-Notebook.jp-mod-commandMode:focus',
      keys: ['0', '0'],
      command: cmdIds.restart
    },
    {
      selector: '.jp-Notebook.jp-mod-commandMode:focus',
      keys: ['Enter'],
      command: cmdIds.editMode
    },
    {
      selector: '.jp-Notebook.jp-mod-editMode',
      keys: ['Escape'],
      command: cmdIds.commandMode
    },
    {
      selector: '.jp-Notebook.jp-mod-commandMode:focus',
      keys: ['Shift M'],
      command: cmdIds.merge
    },
    {
      selector: '.jp-Notebook.jp-mod-editMode',
      keys: ['Ctrl Shift -'],
      command: cmdIds.split
    },
    {
      selector: '.jp-Notebook.jp-mod-commandMode:focus',
      keys: ['J'],
      command: cmdIds.selectBelow
    },
    {
      selector: '.jp-Notebook.jp-mod-commandMode:focus',
      keys: ['ArrowDown'],
      command: cmdIds.selectBelow
    },
    {
      selector: '.jp-Notebook.jp-mod-commandMode:focus',
      keys: ['K'],
      command: cmdIds.selectAbove
    },
    {
      selector: '.jp-Notebook.jp-mod-commandMode:focus',
      keys: ['ArrowUp'],
      command: cmdIds.selectAbove
    },
    {
      selector: '.jp-Notebook.jp-mod-commandMode:focus',
      keys: ['Shift K'],
      command: cmdIds.extendAbove
    },
    {
      selector: '.jp-Notebook.jp-mod-commandMode:focus',
      keys: ['Shift J'],
      command: cmdIds.extendBelow
    },
    {
      selector: '.jp-Notebook.jp-mod-commandMode:focus',
      keys: ['Z'],
      command: cmdIds.undo
    },
    {
      selector: '.jp-Notebook.jp-mod-commandMode:focus',
      keys: ['Y'],
      command: cmdIds.redo
    }
  ];
  bindings.map(binding => commands.addKeyBinding(binding));

  // Create Edit menu.
  let editMenu = new Menu({ commands });
  editMenu.title.label = 'Edit';
  editMenu.insertItem(0, { command: cmdIds.undo });
  editMenu.insertItem(1, { command: cmdIds.redo });
  editMenu.insertItem(2, { type: 'separator' });
  editMenu.insertItem(3, { command: cmdIds.cut });
  editMenu.insertItem(4, { command: cmdIds.copy });
  editMenu.insertItem(5, { command: cmdIds.pasteAbove });
  editMenu.insertItem(6, { command: cmdIds.pasteBelow});
  editMenu.insertItem(7, { command: cmdIds.pasteAndReplace });
  editMenu.insertItem(8, { type: 'separator' });
  editMenu.insertItem(9, { command: cmdIds.deleteCell });
  editMenu.insertItem(10, { type: 'separator' });
  editMenu.insertItem(11, { command: cmdIds.moveUp });
  editMenu.insertItem(12, { command: cmdIds.moveDown });
  editMenu.insertItem(13, { type: 'separator' });
  editMenu.insertItem(14, { command: cmdIds.split});
  editMenu.insertItem(15, { command: cmdIds.merge});
  editMenu.insertItem(16, { type: 'separator' });
  editMenu.insertItem(17, { command: cmdIds.clearOutputs });
  editMenu.insertItem(18, { command: cmdIds.clearAllOutputs });

  // Create Run menu.
  let runMenu = new Menu({ commands });
  runMenu.title.label = 'Run';
  runMenu.insertItem(0, { command: cmdIds.runAndAdvance });
  runMenu.insertItem(1, { command: cmdIds.run });
  runMenu.insertItem(2, { command: cmdIds.runAndInsert });
  runMenu.insertItem(3, { command: cmdIds.runAllAbove });
  runMenu.insertItem(4, { command: cmdIds.runAllBelow });
  runMenu.insertItem(5, { command: cmdIds.renderAllMarkdown });
  runMenu.insertItem(6, { command: cmdIds.runAll });
  runMenu.insertItem(7, { command: cmdIds.restartRunAll });

  // Insert menus in menu bar.
  menuBar.insertMenu(0, editMenu);
  menuBar.insertMenu(1, runMenu);
};
