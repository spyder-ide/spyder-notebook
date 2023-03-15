// Copyright (c) Spyder Project Contributors.
// Distributed under the terms of the Modified BSD License.

import { NotebookApp, NotebookShell } from '@jupyter-notebook/application';

export class SpyderNotebookApp extends NotebookApp {
  /**
   * Construct a new SpyderNotebookApp object.
   *
   * @param options The instantiation options for an application.
   */
  constructor(options: NotebookApp.IOptions = { shell: new NotebookShell() }) {
    super({ ...options, shell: options.shell ?? new NotebookShell() });
  }
}
