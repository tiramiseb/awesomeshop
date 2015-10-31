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

from flask import redirect, url_for

from .. import app
from ..rendering import render_front
from .models import Page

@app.route('/info')
@app.route('/info/')
def info_root():
    return redirect(url_for('doc', slug='about'))

@app.route('/info/<slug>')
def info(slug):
    page = Page.objects.get_or_404(slug=slug, pagetype='info')
    return render_front('page/page.html', page=page, active=page.id)

@app.route('/doc')
@app.route('/doc/')
def doc_root():
    return redirect(url_for('doc', slug='index'))

@app.route('/doc/<slug>')
def doc(slug):
    page = Page.objects.get_or_404(slug=slug, pagetype='doc')
    return render_front('page/page.html', page=page, active=page.id)
