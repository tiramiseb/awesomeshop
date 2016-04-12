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
import docutils.core
from decimal import Decimal

from satchless.item import StockedItem
import prices

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
                            db.ReferenceField(
                                'self',
                                reverse_delete_rule=db.PULL
                                ),
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

    @property
    def related_products_on_sale(self):
        return [p for p in self.related_products if p.on_sale]

    @property
    def path(self):
        return '{}/{}'.format(self.category.path, self.slug)

    @property
    def net_price(self):
        return (self.gross_price * Decimal(1 + self.tax.rate)).quantize(
                                                                Decimal('1.00')
                                                                )

    def get_price_per_item(self, data=None):
        return prices.Price(self.net_price, self.gross_price)

    def remove_quantity(self, quantity):
        """Remove the given quantity or less if the stock is not enough"""
        if self.on_demand:
            from_stock = min(quantity, self.stock)
            on_demand = True
        else:
            quantity = min(quantity, self.stock)
            from_stock = quantity
            on_demand = False
        self.stock = self.stock - from_stock
        self.save()
        return (quantity, from_stock, on_demand)

    def add_to_stock(self, quantity, data=None):
        self.stock += min(quantity, self.stock)

    @property
    def main_photo(self):
        if self.photos:
            return self.photos[0]

    @property
    def description_content(self):
        """Return the formatted content of the description"""
        parts = docutils.core.publish_parts(
                    source=self.description.get(get_locale(), u''),
                    settings_overrides={
                        'initial_header_level': 2
                        },
                    writer_name='html')
        return parts['body']

    @property
    def documentation_content(self):
        """Return the formatted content of the documentation"""
        parts = docutils.core.publish_parts(
                    source=self.documentation.text.get(get_locale(), u''),
                    settings_overrides={
                        'initial_header_level': 3
                        },
                    writer_name='html')
        return parts['body']
