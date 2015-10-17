from flask.ext.babel import lazy_gettext
from flask.ext.wtf import Form
from wtforms.fields import PasswordField, StringField
from wtforms.validators import Email, EqualTo, InputRequired

from .models import Address
from ..mongo import model_form

class LoginForm(Form):
    email = StringField(lazy_gettext('Email address'),
                        validators=[InputRequired()])
    password = PasswordField(
            lazy_gettext('Password'),
            validators=[InputRequired()])


class RegisterForm(Form):
    email = StringField(
                lazy_gettext('Email address'),
                validators=[InputRequired(), Email()])
    password = PasswordField(
                lazy_gettext('Password'),
                validators=[InputRequired()])
    password_again = PasswordField(
                        lazy_gettext('Password (again)'),
                        validators=[
                            InputRequired(),
                            EqualTo(
                                'password_again',
                                lazy_gettext('Passwords must be identical.'))])


class EmailPasswordForm(Form):
    email = StringField(lazy_gettext('Email address'), validators=[Email()])
    password = PasswordField(lazy_gettext('New password'))
    password_again = PasswordField(
            lazy_gettext('New password (again)'),
            validators=[EqualTo(
                   'password_again',
                   lazy_gettext('Passwords must be identical.'))])


AddressForm = model_form(Address, exclude=['user'])
