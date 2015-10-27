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

from flask import Flask, request, session
from flask.ext.babel import Babel
from flask.ext.login import current_user
from flask.ext.mongoengine import MongoEngine


app = Flask(__name__)
app.config.from_object('awesomeshop.defaultconfig')
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
            # If there is no "best match", try pseudo-manually (but ignore weights)
            for i in request.accept_languages.itervalues():
                if '-' in i:
                    i = i.split('-')[0]
                if i in app.config['LANGS']:
                    locale = i
                    break
        except:
            pass
    if not locale:
        # Fallback locale
        locale = app.config['LANGS'][0]
    return locale

# Initialize the debug toolbar when in debug mode
if app.config['DEBUG']:
    app.config['DEBUG_TB_PANELS'] = [
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask.ext.mongoengine.panels.MongoDebugPanel'
        ]
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)

# Initialize flask-login (code must not directly be here
# or there is an import loop)
from . import auth 

# Imports views only in order to make them available
from .auth import views
from .dashboard import views
from .home import views
from .page import views
from .payment import views
from .shop import views
from . import error_views
