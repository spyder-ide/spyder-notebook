# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder_notebook/__init__.py for details)

"""Variant of Spyder's kernel spec for the use in the notebook server."""

# Third-party import
from spyder.plugins.ipythonconsole.utils.kernelspec import SpyderKernelSpec


class SpyderNotebookKernelSpec(SpyderKernelSpec):
    """Variant of SpyderKernelSpec which specifies our provisioner"""

    metadata = {
        'kernel_provisioner': {'provisioner_name': 'spyder-local-provisioner'}
    }
