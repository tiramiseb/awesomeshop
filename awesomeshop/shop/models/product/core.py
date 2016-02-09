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

from satchless.item import StockedItem

from .... import db, get_locale
from ....mongo import TranslationsField
from ....photo import Photo
from ....page.models import Page
from ..category import Category
from ..tax import Tax


class BaseProduct(db.Document, StockedItem):
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
    meta = {
        'collection': 'product',
        'ordering': ['reference'],
        'allow_inheritance': True
    }
    
    @property
    def loc_name(self):
        return self.name.get(get_locale(), u'')

    def get_full_name(self, data=None):
        """Get the product full name, including data
        
        Must return a string"""
        raise NotImplementedError

    def get_price_per_item(self, data=None):
        """Returns the price of this product with the given data
        
        Must return a prices.Price object"""
        raise NotImplementedError
