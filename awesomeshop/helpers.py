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

from flask import abort, current_app, render_template as orig_render_template
from flask.ext.babel import lazy_gettext
from flask.ext.login import current_user, fresh_login_required, login_required

from . import db, get_locale
from .shop.cart import Cart
from .page.models import Page
from .shop.models import Category


def render_template(template, **context):
    context['locale'] = get_locale()
    return orig_render_template(template, **context)

def render_front(template, **context):
    context['categories'] = Category.hierarchy()
    context['infopages'] = Page.objects(pagetype='info', in_menu=True)
    context['docpages'] = Page.objects(pagetype='doc', in_menu=True)
    context['cart'] = Cart.from_session()
    return render_template(template, **context)


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

class Setting(db.Document):
    name = db.StringField(required=True, unique=True, max_length=100,
                          verbose_name=lazy_gettext('Name'))
    value = db.DynamicField()

    def __str__(self):
        return 'Setting: {} = {}'.format(self.name, self.value)
