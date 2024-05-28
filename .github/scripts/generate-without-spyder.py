#!/usr/bin/env python
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""Script to generate requirements/without-spyder.txt"""

import re
from pathlib import Path

rootdir = Path(__file__).parents[2]
input_filename = rootdir / 'requirements' / 'conda.txt'
output_filename = rootdir / 'requirements' / 'without-spyder.txt'

with open(input_filename) as infile:
    with open(output_filename, 'w') as outfile:
        for line in infile:
            package_name = re.match('[-a-z0-9_]*', line).group(0)
            if package_name != 'spyder':
                outfile.write(line)
