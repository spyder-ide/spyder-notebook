// Copyright (c) Jupyter Development Team, Spyder Project Contributors.
// Distributed under the terms of the Modified BSD License.

// Adapted from jupyterlab/packages/tooltip-extension/src/index.ts

import { CodeEditor } from '@jupyterlab/codeeditor';
import { Text } from '@jupyterlab/coreutils';
import { NotebookPanel } from '@jupyterlab/notebook';
import { Kernel, KernelMessage } from '@jupyterlab/services';
import { Tooltip } from '@jupyterlab/tooltip';
import { Widget } from '@phosphor/widgets';
import { JSONObject } from '@phosphor/coreutils';

let tooltip: Tooltip | null = null;

export function dismissTooltip() {
  if (tooltip) {
    tooltip.dispose();
    tooltip = null;
  }
}

export function invokeTooltip(nbWidget: NotebookPanel) {
  const detail: 0 | 1 = 0;
  const parent = nbWidget.context;
  const anchor = nbWidget.content;
  const editor = anchor.activeCell.editor;
  const kernel = parent.session.kernel;
  const rendermime = anchor.rendermime;

  // If some components necessary for rendering don't exist, stop
  if (!editor || !kernel || !rendermime) {
    return;
  }

  if (tooltip) {
    tooltip.dispose();
    tooltip = null;
  }

  return fetchTooltip({ detail, editor, kernel })
    .then(bundle => {
      tooltip = new Tooltip({ anchor, bundle, editor, rendermime });
      Widget.attach(tooltip, document.body);
    })
    .catch(() => {
      /* Fails silently. */
    });
}

// A counter for outstanding requests.
let pending = 0;

interface IFetchOptions {
  /**
   * The detail level requested from the API.
   *
   * #### Notes
   * The only acceptable values are 0 and 1. The default value is 0.
   * @see http://jupyter-client.readthedocs.io/en/latest/messaging.html#introspection
   */
  detail?: 0 | 1;

  /**
   * The referent editor for the tooltip.
   */
  editor: CodeEditor.IEditor;

  /**
   * The kernel against which the API request will be made.
   */
  kernel: Kernel.IKernelConnection;
}

/**
 * Fetch a tooltip's content from the API server.
 */
function fetchTooltip(options: IFetchOptions): Promise<JSONObject> {
  let { detail, editor, kernel } = options;
  let code = editor.model.value.text;
  let position = editor.getCursorPosition();
  let offset = Text.jsIndexToCharIndex(editor.getOffsetAt(position), code);

  // Clear hints if the new text value is empty or kernel is unavailable.
  if (!code || !kernel) {
    return Promise.reject(void 0);
  }

  let contents: KernelMessage.IInspectRequestMsg['content'] = {
    code,
    cursor_pos: offset,
    detail_level: detail || 0
  };
  let current = ++pending;

  return kernel.requestInspect(contents).then(msg => {
    let value = msg.content;

    // If a newer request is pending, bail.
    if (current !== pending) {
      return Promise.reject(void 0) as Promise<JSONObject>;
    }

    // If request fails or returns negative results, bail.
    if (value.status !== 'ok' || !value.found) {
      return Promise.reject(void 0) as Promise<JSONObject>;
    }

    return Promise.resolve(value.data);
  });
}
