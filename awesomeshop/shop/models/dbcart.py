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

from ... import db
from ...auth.models import User
from .product import Product


class DbCartline(db.EmbeddedDocument):
    product = db.ReferenceField(Product, db_field='prod')
    quantity = db.IntField(db_field='qty')
    data = db.DictField()

    @property
    def unit_price(self):
        return self.product.get_price_per_item(self.data)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def get_total(self):
        return self.product.get_price_per_item() * self.quantity


class DbCart(db.Document):
    user = db.ReferenceField(User, required=True)
    date = db.DateTimeField(default=datetime.datetime.now)
    name = db.StringField()
    lines = db.EmbeddedDocumentListField(DbCartline)

    meta = {
        'collection': 'cart',
        'ordering': ['-date']
    }

    @property
    def total_price(self):
        price = prices.Price(0)
        for line in self.lines:
            price += line.get_total()
        return price
