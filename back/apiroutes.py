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

from flask import jsonify, make_response, redirect, request
from flask_login import current_user
from flask_restful import Resource

from .shop.models.order import Order
from . import app, login_required, pdf, rest

# TODO Move everything somewhere in "/api"

@app.route('/confirm/<code>')
@login_required
def confirm_email(code):
    if code == current_user.confirm_code:
        current_user.confirm_code = None
        current_user.save()
    # TODO Redirect the user to a specific message
    return redirect('/')


class ApiConfig(Resource):
    def get(self):
        return jsonify(
                confirm_delay=app.config['CONFIRM_DELAY'],
                currency=app.config['CURRENCY'],
                home=app.config['HOME_CONTENT'],
                languages=app.config['LANGS'],
                logo=app.config['LOGO_CONTENT'],
                payment_delay=app.config['PAYMENT_DELAY'],
                shop_description=app.config['SHOP_DESCRIPTION'],
                shop_name=app.config['SHOP_NAME'],
                social=app.config['SOCIAL'],
                )

class ApiSearch(Resource):
    def get(self):
        from .search import do_search
        terms = request.args.get('terms', u'')
        return do_search(terms)

rest.add_resource(ApiSearch, '/search')
rest.add_resource(ApiConfig, '/config')


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

from .auth import api
from .page import api
from .payment import api
from .shipping import api
from .shop.api import category, dbcart, order, product, tax
