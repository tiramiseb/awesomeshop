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
"""Run AwesomeShop locally for development"""

from flask.helpers import send_from_directory
from werkzeug.exceptions import NotFound

from back import create_app

app = create_app(prefix='/api')
app.debug = True

@app.route('/')
@app.route('/<path:path>')
def static_file(path=None):
    if not path:
        path = 'index.html'
    try:
        return send_from_directory('webroot', path)
    except NotFound:
        return static_file()

app.run()

