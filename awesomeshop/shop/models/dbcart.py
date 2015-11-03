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

import datetime

import prices
from flask import session
from flask.ext.login import current_user

from ... import db
from ...auth.models import User
from .product import BaseProduct



class DbCartLine(db.EmbeddedDocument):
    product = db.ReferenceField(BaseProduct, db_field='prod')
    quantity = db.IntField(db_field='qty')
    data = db.DictField()

    @property
    def available_quantity(self):
        if self.product.on_demand:
            return self.quantity
        else:
            return min(self.product.stock, self.quantity)

    def get_price_per_item(self, **kwargs):
        return self.product.get_price(data=self.data, **kwargs)

    def get_total(self):
        return self.get_price_per_item() * self.available_quantity

    def for_session(self):
        return {
            'product_id': str(self.product.id),
            'quantity': self.available_quantity,
            'data': self.data
            }

    def get_full_name(self):
        return self.product.get_full_name(self.data)

class DbCart(db.Document):
    user = db.ReferenceField(User, required=True)
    date = db.DateTimeField(default=datetime.datetime.now)
    name = db.StringField()
    lines = db.EmbeddedDocumentListField(DbCartLine)

    meta = {
        'collection': 'cart',
        'ordering': ['-date']
    }

    @classmethod
    def from_sessioncart(cls, sessioncart, name=None):
        if not name:
            name = _('Unnamed cart')
        dbcart = cls(name=name, user=current_user.to_dbref())
        for line in sessioncart:
            dbcart.lines.append(
                            DbCartLine(
                                    product=line.product,
                                    quantity=line.quantity
                                    )
                            )
        return dbcart

    def to_session(self):
        lines = [ line.for_session() for line in self.lines ]
        session['cart'] = [ line for line in lines if line ]

    @property
    def formated_date(self):
        return self.date.strftime('%d/%m/%Y')

    @property
    def total_quantity(self):
        qty = 0
        for line in self.lines:
            qty += line.available_quantity
        return qty

    @property
    def total_price(self):
        price = prices.Price(0)
        for line in self.lines:
            price += line.get_total()*line.available_quantity
        return price
