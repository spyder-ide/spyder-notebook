# Copyright (c) Jupyter Development Team, Spyder Project Contributors.
# Distributed under the terms of the Modified BSD License.

"""Entry point for server rendering notebooks for Spyder."""

# Standard library imports
import os
import signal
import sys

# Third-party imports
from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client.provisioning.local_provisioner import LocalProvisioner
from jupyter_server.serverapp import ServerApp
from notebook.app import (
    aliases, flags, JupyterNotebookApp, NotebookBaseHandler)
import psutil
from tornado import web
from traitlets import default, Bool, Type, Unicode


HERE = os.path.dirname(__file__)

aliases['info-file'] = 'SpyderNotebookApp.info_file_cmdline'

flags['dark'] = (
    {'SpyderNotebookApp': {'dark_theme': True}},
    'Use dark theme when rendering notebooks'
)


class SpyderNotebookHandler(NotebookBaseHandler):
    """A notebook page handler for Spyder."""

    def get_page_config(self):
        page_config = super().get_page_config()
        page_config['darkTheme'] = self.extensionapp.dark_theme
        page_config['disabledExtensions'] = [
            # Remove editor-related items from Settings menu
            '@jupyterlab/fileeditor-extension',
            # Remove items Open JupyterLab and File Browser from View menu
            '@jupyter-notebook/application-extension:pages',
            # Remove toolbar button Interface > Open With JupyterLab
            '@jupyter-notebook/lab-extension:interface-switcher',
            # Remove Launch Jupyter Notebook File Browser from Help menu
            '@jupyter-notebook/lab-extension:launch-tree'
        ]
        return page_config

    @web.authenticated
    def get(self, path=None):
        """Get the notebook page."""
        tpl = self.render_template(
            'notebook-template.html', page_config=self.get_page_config())
        return self.write(tpl)


class SpyderLocalProvisioner(LocalProvisioner):
    """Variant of Jupyter's LocalProvisioner for Spyder kernels"""

    async def send_signal(self, signum):
        """
        Send signal to kernel.

        For Jupyter Python kernels, the PID in self.pid is the Python process.
        However, Spyder kernels may use `conda run` to start the Pyhon process
        in the correct environment. In that case, self.pid is the PID of the
        `conda run` process. The `conda run` command starts a shell which in
        turn starts the kernel process.

        When the user wants to interrupt the kernel, Jupyter wants to send
        SIGINT to self.pid, but for Spyder kernels started with `conda run`
        we need to send SIGINT to the grandchild of self.pid.
        """
        if signum == signal.SIGINT and sys.platform != "win32":
            # Windows is handled differently in LocalProvisioner
            try:
                process = psutil.Process(self.pid)
                cmdline = process.cmdline()
                if len(cmdline) > 2 and cmdline[2] == 'run':
                    # If second word on command line is 'run', then assume
                    # kernel is started with 'conda run' and therefore
                    # send SIGINT to grandchild.
                    grandchild_pid = process.children()[0].children()[0].pid
                    self.log.info(f'Sending signal to PID {grandchild_pid} '
                                  f'instead of process group of PID {self.pid}')
                    os.kill(grandchild_pid, signum)
                    return
            except (psutil.AccessDenied, psutil.NoSuchProcess, IndexError, OSError):
                # Ignore errors and fall back to code in LocalProvisioner
                pass

        await super().send_signal(signum)


class SpyderKernelSpecManager(KernelSpecManager):
    """Variant of Jupyter's KernelSpecManager"""
    # Ensure that there is only one kernel spec, the default one
    allowed_kernelspecs = 'python3'

    # Ensure that default kernel spec is our own kernel spec.
    # This is given as a string to defer the import.
    kernel_spec_class = Type(
        'spyder_notebook.server.kernelspec.SpyderNotebookKernelSpec'
    )


class SpyderServerApp(ServerApp):
    """Variant of Jupyter's ServerApp"""
    kernel_spec_manager_class = SpyderKernelSpecManager


class SpyderNotebookApp(JupyterNotebookApp):
    """The Spyder notebook server extension app."""

    name = 'spyder_notebook'
    app_name = "Spyder/Jupyter Notebook"
    description = "Spyder/Jupyter Notebook - A variant of Jupyter Notebook to be used inside Spyder"
    file_url_prefix = "/spyder-notebooks"

    # Replace Jupyter's ServerApp with our own
    serverapp_class = SpyderServerApp

    # Do not open web browser when starting app
    open_browser = False

    flags = dict(flags)
    aliases = dict(aliases)

    dark_theme = Bool(
        False, config=True,
        help='Whether to use dark theme when rendering notebooks')

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
        self.handlers.append(('/spyder-notebooks(.*)', SpyderNotebookHandler))
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
