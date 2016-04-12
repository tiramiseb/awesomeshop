# -*- coding: utf8 -*-

# Copyright 2015-2016 Sébastien Maccagnoni-Munch
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

import base64
import datetime
import uuid
from flask_login import UserMixin
from os import urandom
from scrypt import hash as scrypt_hash

from .. import db
from ..mail import send_mail
from ..shipping.models import Country


class User(db.Document, UserMixin):
    created_at = db.DateTimeField(db_field='create',
                                  default=datetime.datetime.now, required=True)
    email = db.EmailField(unique=True)
    passsalt = db.StringField(db_field='salt')
    passhash = db.StringField(db_field='hash')
    is_admin = db.BooleanField(db_field='adm', default=False)
    locale = db.StringField()
    confirm_code = db.StringField(db_field='confirm')
    # The following are the user's "preferences" from his latest order
    latest_delivery_address = db.StringField(db_field='del_addr')
    latest_billing_address = db.StringField(db_field='bil_addr')
    latest_delivery_as_billing = db.BooleanField(db_field='del_as_bil',
                                                 default=True)
    latest_carrier = db.StringField(db_field='carrier')
    latest_payment = db.StringField(db_field='paymt')
    latest_reused_package = db.BooleanField(db_field='reuse_pkg')

    meta = {
        'ordering': ['email']
    }

    @property
    def addresses(self):
        return Address.objects(user=self)

    @property
    def carts(self):
        from ..shop.models import DbCart
        return DbCart.objects(user=self)

    def set_password(self, password):
        salt = base64.b64encode(urandom(64))
        self.passsalt = salt
        self.passhash = base64.b64encode(
                scrypt_hash(
                    password.encode('utf-8'),
                    salt.encode('utf-8')))

    def check_password(self, password):
        candidate_hash = base64.b64encode(
                scrypt_hash(
                    password.encode('utf-8'),
                    self.passsalt.encode('utf-8')))
        return self.passhash.encode('utf-8') == candidate_hash

    def send_confirmation_email(self):
        self.confirm_code = str(uuid.uuid4())
        send_mail(self.email, 'email_confirmation', code=self.confirm_code)


class Address(db.Document):
    user = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    title = db.StringField()
    firstname = db.StringField(db_field='fname')
    lastname = db.StringField(db_field='lname')
    address = db.StringField(db_field='addr')
    country = db.ReferenceField(Country, reverse_delete_rule=db.DENY)
    phone = db.StringField(default='')

    meta = {
        'ordering': ['title']
    }

    @property
    def human_readable(self):
        return u'{} {}\n{}\n{}'.format(
                self.firstname,
                self.lastname,
                self.address,
                self.country.prefixed_name)
