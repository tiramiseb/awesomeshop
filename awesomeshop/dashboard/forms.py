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
from wtforms.fields import BooleanField, StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired

from ..mongo import model_form
from ..auth.models import User, Address
from ..page.models import Page
from ..shipping.models import Country, CountriesGroup, Carrier
from ..shop.models import Tax, Category, Product

UserForm = model_form(User)
class UserForm(Form):
    email = StringField(lazy_gettext('Email address'),
                        validators=[InputRequired(), Email()])
    is_admin = BooleanField(lazy_gettext('Is an administrator'))
    password = PasswordField(lazy_gettext('Password'), validators=[
                            EqualTo(
                                'password_again',
                                lazy_gettext('Passwords must be identical.'))
                            ])
    password_again = PasswordField(lazy_gettext('Password (again)'))

AddressForm = model_form(Address, exclude=['user'])

CountryForm = model_form(Country)
CountriesGroupForm = model_form(CountriesGroup)

CarrierForm = model_form(Carrier, field_args={
    'weights': {
        'min_entries': 1
        }
    })

TaxForm = model_form(Tax)

CategoryForm = model_form(Category, field_args={
    'parent': {
        'allow_blank': True
        }
    })

ProductForm = model_form(Product)
def get_product_form(form, prod):
    if type(prod) == Product:
        return ProductForm(form, prod)
    return None

PageForm = model_form(Page)

