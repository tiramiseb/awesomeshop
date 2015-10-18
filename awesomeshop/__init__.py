#!/usr/bin/env python

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
    if from_user and current_user and current_user.is_authenticated \
            and current_user.locale:
        return current_user.locale
    try:
        return session.get('locale') or \
               request.accept_languages.best_match(app.config['LANGS'])
    except RuntimeError:
        return app.config['LANGS'][0]

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
