# -*- coding: utf8 -*-

# Copyright 2015-2016 Sébastien Maccagnoni
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
"""AwesomeShop: an e-commerce webapp using Flask"""

from functools import wraps

from flask import abort, current_app, Flask, make_response, request, session
from flask_login import current_user, LoginManager, login_required
from flask_mongoengine import MongoEngine
from flask_restful import Api
import simplejson


def create_app(prefix=''):
    global app
    global db
    global rest
    app = Flask('awesomeshop')
    app.config.from_object('back.defaultconfig')
    rest = Api(app, prefix=prefix, catch_all_404s=True)
    @rest.representation('application/json')
    def output_json(data, code, headers=None):
        resp = make_response(simplejson.dumps(data) + "\n", code)
        resp.headers.extend(headers or {})
        return resp
    try:
        app.config.from_object('config')
    except ImportError:
        print 'Could not load your configuration file!'
        print 'Please create "config.py" where you run AwesomeShop...'
        import sys
        sys.exit(1)
    db = MongoEngine(app)
    login_manager = LoginManager(app)
    @login_manager.user_loader
    def load_user(uid):
        from .auth.models import User
        try:
            return User.objects.get(id=uid)
        except User.DoesNotExist:
            return None
    from . import autoupgrade
    autoupgrade.upgrade()
    from . import apiroutes
    return app


def get_locale():
    return request.args.get('lang', app.config['LANGS'][0])


def admin_required(func):
    """Decorator when a request can only be made by admins

    Inspired by flask_login.login_required
    """
    @wraps(func)
    @login_required
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled or current_user.is_admin:
            return func(*args, **kwargs)
        abort(403)
    return decorated_view
