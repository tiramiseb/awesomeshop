
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

import datetime

from satchless.item import StockedItem

from ... import db, get_locale
from ...mongo import TranslationsField
from ...photo import Photo
from ...page.models import Page
from .category import Category
from .tax import Tax

class Product(db.Document, StockedItem):
    created_at = db.DateTimeField(db_field='create',
                                  default=datetime.datetime.now)
    slug = db.StringField()
    reference = db.StringField(db_field='ref')
    name = TranslationsField()
    description = TranslationsField(db_field='desc')
    documentation = db.ReferenceField(
                            Page,
                            db_field='doc',
                            reverse_delete_rule=db.DENY
                            )
    category = db.ReferenceField(Category, db_field='cat',
                                 reverse_delete_rule=db.DENY)
    keywords = db.StringField(db_field='kw')
    photos = db.EmbeddedDocumentListField(Photo)
    tax = db.ReferenceField(Tax, reverse_delete_rule=db.DENY)
    on_sale = db.BooleanField(db_field='sale')
    related_products = db.ListField(
                            db.ReferenceField('self'),
                            db_field='rel',
                            )
    on_demand = db.BooleanField(db_field='dem')
    purchasing_price = db.DecimalField(db_field='pprice')
    gross_price = db.DecimalField(db_field='gprice')
    weight = db.IntField()
    stock = db.IntField()
    stock_alert = db.IntField(db_field='alert')

    meta = {
        'ordering': ['reference']
    }

    def get_price_per_item(self, data=None):
        gross = self.gross_price
        net = gross * ( 1 + self.tax.rate )
        return prices.Price(net, gross)
