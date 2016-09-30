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
"""Automatic generation of HTML files from PLIM sources"""

import os
import re

from inotify.adapters import InotifyTree
from plim import preprocessor

FROM='front'
TO='webroot'

i = InotifyTree(FROM)
for event in i.event_gen():
    if event is not None and 'IN_CLOSE_WRITE' in event[1]:
        if event[3].endswith('.plim'):
            filename = os.path.join(event[2], event[3])
            target = re.sub(FROM+'/(.*).plim', TO+r'/\1.html', filename)
            dirname = os.path.dirname(target)
            result = preprocessor(file(filename, 'r').read())
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            file(target, 'w').write(result)
            print "Regenerated", target
