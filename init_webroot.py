#!/usr/bin/env python
# -*- coding: utf8 -*-

# Copyright 2016 Sébastien Maccagnoni
#
# This file is part of AwesomeShop.
#
# AwesomeShop is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# AwesomeShop is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with AwesomeShop. If not, see <http://www.gnu.org/licenses/>.
"""Prepare webroot : install libs from bower and generate HTML form PLIM"""

import os
import shutil
import subprocess

from plim import preprocessor

FROM='front'
TO='webroot'

# First copy files and generate HTML from PLIM
for parent, dirs, files in os.walk(FROM):
    targetdir = parent.replace(FROM, TO, 1)
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    for filename in files:
        sourcefile = os.path.join(parent, filename)
        if filename.endswith('.plim'):
            destfile = os.path.join(targetdir,
                                    filename.replace('.plim', '.html'))
            result = preprocessor(file(sourcefile, 'r').read())
            file(destfile, 'w').write(result)
            print "Generated", destfile
        else:
            destfile = os.path.join(targetdir, filename)
            shutil.copyfile(sourcefile, destfile)
            print "Copied", sourcefile

# Then install libs with bower
os.chdir(TO)
subprocess.call(['bower', 'install'])
