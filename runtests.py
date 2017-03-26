# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""
File for running tests programmatically.
"""

# Third party imports
import pytest


def main():
    """
    Run pytest tests.
    """
    errno = pytest.main(['-x', 'spyder_notebook',  '-v', '-rw', '--durations=10',
                         '--cov=spyder_notebook', '--cov-report=term-missing'])

    # sys.exit doesn't work here because some things could be running
    # in the background (e.g. closing the main window) when this point
    # is reached. And if that's the case, sys.exit does't stop the
    # script (as you would expected).
    if errno != 0:
        raise SystemExit(errno)

if __name__ == '__main__':
    main()
