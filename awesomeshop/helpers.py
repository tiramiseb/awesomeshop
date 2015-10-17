from functools import wraps

from flask import abort, current_app, render_template as orig_render_template
from flask.ext.login import current_user, fresh_login_required, login_required

from . import get_locale
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

