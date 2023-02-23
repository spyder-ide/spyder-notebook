// Copyright (c) Spyder Project Contributors.
// Distributed under the terms of the Modified BSD License.

import { NotebookShell } from '@jupyter-notebook/application';

/**
 * The application shell.
 *
 * Changes from Jupyter Notebook:
 * - Always hide the top panel
 */
export class SpyderNotebookShell extends NotebookShell {
  constructor() {
    super();
    this.collapseTop();
  }

  /**
   * Overridden to do nothing
   */
  expandTop(): void {
  }
}
