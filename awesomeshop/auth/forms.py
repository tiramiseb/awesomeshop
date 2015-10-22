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
