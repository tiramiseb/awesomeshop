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

from flask import abort, jsonify, redirect, render_template, request
from flask.ext.login import current_user
from jinja2.exceptions import TemplateNotFound

from . import app, login_required, admin_required

@app.route('/')
def root():
    return ''

@app.route('/login', methods=['GET','POST'])
def login():
#    if current_user.is_authenticated:
#        return redirect(request.args.get('next') or '/')
#    form = LoginForm()
#    if form.validate_on_submit():
#        try:
#            user = User.objects.get(email=form.email.data)
#        except User.DoesNotExist:
#            user = None
#        if user and user.check_password(form.password.data):
#            login_user(user)
#            return redirect(request.args.get('next') or url_for('home'))
#        form.email.errors.append(_('Email address or Password is invalid.'))
    return render_template('login.html')

@app.route('/part/<partname>')
def part(partname):
    try:
        return render_template('part/{}.html'.format(partname))
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
