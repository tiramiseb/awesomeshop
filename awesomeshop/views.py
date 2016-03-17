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
# along with eAwesomeShop. If not, see <http://www.gnu.org/licenses/>.

from flask import abort, jsonify, redirect, \
                  render_template as orig_render_template, request
from flask_login import current_user
from jinja2.exceptions import TemplateNotFound

from . import app, get_locale, login_required, admin_required, messages

def render_template(template, **context):
    context['locale'] = get_locale()
    return orig_render_template(template, **context)

@app.route('/')
@app.route('/<path:path>')
def shop(path=None):
    return render_template('shop.html')

@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')

@app.route('/messages')
def messages_route():
    return jsonify(messages.messages())

@app.route('/confirm/<code>')
@login_required
def confirm_email(code):
    if code == current_user.confirm_code:
        current_user.confirm_code = None
        current_user.save()
    # XXX Redirect the user to a specific message
    return redirect('/')

@app.route('/part/<partname>')
def part(partname):
    try:
        return render_template('part/{}.html'.format(partname))
    except TemplateNotFound:
        abort(404)

@app.route('/shop/<partname>')
def shop_part(partname):
    try:
        return render_template('shop/{}.html'.format(partname))
    except TemplateNotFound:
        abort(404)

@app.route('/dashboard')
@app.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboard/<partname>')
@admin_required
def dashboard_part(partname):
    try:
        return render_template('dashboard/{}.html'.format(partname))
    except TemplateNotFound:
        abort(404)

@app.route('/api/config')
def api_config():
    return jsonify(
            languages=app.config['LANGS']
            )

@app.errorhandler(401)
def unauthorized(e):
    return jsonify(error='401', message='Unauthorized'), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify(error='403', message='Forbidden'), 403

@app.errorhandler(404)
def notfound(e):
    return jsonify(error='404', message='Not Found'), 404

@app.errorhandler(500)
def internalservererror(e):
    return jsonify(error='500', message='Internal Server Error'), 500
