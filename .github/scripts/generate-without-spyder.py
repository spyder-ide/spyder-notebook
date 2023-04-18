#!/usr/bin/env python
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""Script to generate requirements/without-spyder.txt"""

import re

with open('requirements/conda.txt') as infile:
    with open('requirements/without-spyder.txt', 'w') as outfile:
        for line in infile:
            package_name = re.match('[-a-z0-9_]*', line).group(0)
            if package_name != 'spyder':
                outfile.write(line)

