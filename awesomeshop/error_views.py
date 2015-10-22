# -*- coding: utf8 -*-

# Copyright 2015 Sébastien Maccagnoni-Munch
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

from . import app
from .helpers import render_front

@app.errorhandler(500)
def page_not_found(e):
    return render_front('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_front('404.html'), 404

@app.errorhandler(403)
def page_not_found(e):
    return render_front('403.html'), 403

@app.errorhandler(400)
def page_not_found(e):
    return render_front('400.html'), 400

