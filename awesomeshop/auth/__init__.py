from flask.ext.login import LoginManager

from .. import app
from .models import User


login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = None

@login_manager.user_loader
def load_user(uid):
    try:
        return User.objects.get(id=uid)
    except User.DoesNotExist:
        return None

