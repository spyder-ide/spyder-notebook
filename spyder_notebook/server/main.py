# Copyright (c) Jupyter Development Team, Spyder Project Contributors.
# Distributed under the terms of the Modified BSD License.

"""Entry point for server rendering notebooks for Spyder."""

import os
from notebook.app import aliases, JupyterNotebookApp, NotebookBaseHandler
from tornado import web
from traitlets import default, Unicode

HERE = os.path.dirname(__file__)

aliases['info-file'] = 'SpyderNotebookApp.info_file_cmdline'


class SpyderNotebookHandler(NotebookBaseHandler):
    """A notebook page handler for Spyder."""

    @web.authenticated
    def get(self, path=None):
        """Get the notebook page."""
        tpl = self.render_template(
            'notebook-template.html', page_config=self.get_page_config())
        return self.write(tpl)


class SpyderNotebookApp(JupyterNotebookApp):
    """The Spyder notebook server extension app."""

    name = 'spyder_notebook'
    file_url_prefix = "/notebooks"

    aliases = dict(aliases)
    info_file_cmdline = Unicode(
        '', config=True,
        help='Name of file in Jupyter runtime dir with connection info')

    @default('static_dir')
    def _default_static_dir(self):
        return os.path.join(HERE, 'static')

    @default('templates_dir')
    def _default_templates_dir(self):
        return HERE

    def initialize_handlers(self):
        """Initialize handlers."""
        self.handlers.append(('/notebooks(.*)', SpyderNotebookHandler))
        super().initialize_handlers()

    @classmethod
    def _load_jupyter_server_extension(cls, serverapp):
        """
        Overridden to propagate `info-file` command line parameter.

        If the `info-file` command line parameter is given, then prepend the
        Jupyter runtime directory and use the resulting path to store the
        server info file.
        """
        extension = super()._load_jupyter_server_extension(serverapp)
        if extension.info_file_cmdline:
            serverapp.info_file = os.path.join(
                serverapp.runtime_dir, extension.info_file_cmdline)
        return extension

main = SpyderNotebookApp.launch_instance

if __name__ == "__main__":
    main()
