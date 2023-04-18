// Copyright (c) Spyder Project Contributors.
// Distributed under the terms of the Modified BSD License.

import { NotebookApp } from '@jupyter-notebook/application';

import { SpyderNotebookShell } from './shell';

/**
 * App is the main application class. It is instantiated once and shared.
 *
 * Changes from Jupyter Notebook:
 * - Use our SpyderNotebookShell instead of Jupyter's NotebookShell
 */
export class SpyderNotebookApp extends NotebookApp {
  /**
   * Construct a new SpyderNotebookApp object.
   *
   * @param options The instantiation options for an application.
   */
  constructor(options: NotebookApp.IOptions = { shell: new SpyderNotebookShell() }) {
    super({ ...options, shell: options.shell ?? new SpyderNotebookShell() });
  }
}
