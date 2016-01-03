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

from functools import wraps

from flask import abort, current_app, Flask, request, session
from flask.ext.babel import Babel
from flask.ext.login import current_user, LoginManager, login_required
from flask.ext.mongoengine import MongoEngine
from flask_restful import Api

app = Flask(__name__)
app.config.from_object('awesomeshop.defaultconfig')
rest = Api(app, catch_all_404s=True)
try:
    app.config.from_object('config')
except ImportError:
    print 'Could not load your configuration file!'
    print 'Please create "config.py" where you run AwesomeShop...'
    import sys
    sys.exit(1)
db = MongoEngine(app)

# Initialize flask-babel
babel = Babel(app)
@babel.localeselector
def get_locale(from_user=True):
    locale = None
    if from_user and current_user and current_user.is_authenticated \
            and current_user.locale:
        # Use the user-defined locale if it exists
        locale = current_user.locale
    else:
        try:
            # Use the locale defined in the session or get the "best match"
            locale = session.get('locale') or \
                     request.accept_languages.best_match(app.config['LANGS'])
        except:
            pass
    if not locale:
        try:
            # If there is no "best match", try pseudo-manually (ignore weights)
            for i in request.accept_languages.itervalues():
                if '-' in i:
                    i = i.split('-')[0]
                if i in app.config['LANGS']:
                    locale = i
                    break
        except:
            pass
    if not locale:
        # Fallback locale, defined app-wide
        locale = app.config['LANGS'][0]
    return locale
app.jinja_env.globals.update(get_locale=get_locale)

login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(uid):
    from .auth.models import User
    try:
        return User.objects.get(id=uid)
    except User.DoesNotExist:
        return None
def admin_required(func):
    """Decorator when a request can only be made by admins
    
    Inspired by flask.ext.login.login_required
    """
    @wraps(func)
    @login_required
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled or current_user.is_admin:
            return func(*args, **kwargs)
        abort(403)
    return decorated_view

###############################################################################

from . import autoupgrade
autoupgrade.upgrade()

###############################################################################

import views
from auth import api
from page import api
from shipping import api
