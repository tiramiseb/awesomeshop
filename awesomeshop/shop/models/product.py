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

import docutils.core
import prices
from flask.ext.babel import lazy_gettext
from satchless.item import StockedItem

from ... import db, get_locale
from ...mongo import TranslationsField
from ...photo import Photo
from ...page.models import Page
from .category import Category
from .tax import Tax

# When adding a new product type:
#
# * it should inherit from BaseProduct
# * unless otherwise stated, all functions raising NotImplementedError must be
#   overriden
# * a new entry must be added to the product_types dict
# * signals must be added in .shop_signals, copying signals for Product

class BaseProduct(db.Document, StockedItem):
    created_at = db.DateTimeField(db_field='create',
                                  default=datetime.datetime.now, required=True)
    slug = db.StringField(required=True, max_length=50,
                          verbose_name=lazy_gettext('Slug'))
    reference = db.StringField(db_field='ref',
                               max_length=50, unique=True, required=True,
                               verbose_name=lazy_gettext('Reference'))
    name = TranslationsField(max_length=100, verbose_name=lazy_gettext('Name'))
    description = TranslationsField(db_field='desc',
                                    verbose_name=lazy_gettext('Description'))
    documentation = db.ReferenceField(
                            Page,
                            db_field='doc',
                            reverse_delete_rule=db.DENY,
                            verbose_name=lazy_gettext('Documentation')
                            )
    category = db.ReferenceField(Category, db_field='cat',
                                 reverse_delete_rule=db.DENY,
                                 verbose_name=lazy_gettext('Category'))
    keywords = db.StringField(db_field='kw', max_length=200,
                              verbose_name=lazy_gettext('Keywords'))
    photos = db.EmbeddedDocumentListField(Photo)
    tax = db.ReferenceField(Tax,
                            reverse_delete_rule=db.DENY,
                            verbose_name=lazy_gettext('Tax'))
    on_sale = db.BooleanField(db_field='sale',
                              verbose_name=lazy_gettext('Is on sale'))
    related_products = db.ListField(
                            db.ReferenceField('self'),
                            db_field='rel',
                            verbose_name=lazy_gettext('Related products')
                            )
    on_demand = db.BooleanField(
                        db_field='dem',
                        default=False,
                        verbose_name=lazy_gettext('On demand')
                        )
    meta = {
        'collection': 'product',
        'ordering': ['reference'],
        'allow_inheritance': True
    }

    def __unicode__(self):
        return self.name.get(get_locale(), u'')

    def __repr__(self):
        return unicode(self).encode('utf8')

    @property
    def output_description(self):
        parts = docutils.core.publish_parts(
                    source=self.description.get(get_locale(), u''),
                    writer_name='html')
        return parts['body']

    @property
    def output_documentation(self):
        parts = docutils.core.publish_parts(
                    source=self.documentation.text.get(get_locale(), u''),
                    settings_overrides = {
                        'initial_header_level': 3
                        },
                    writer_name='html')
        return parts['body']

    @property
    def url(self):
        from .url import Url
        return Url.objects(document=self).only('url').first().url

    @property
    def type(self):
        return product_to_type[self.__class__]

    @property
    def human_type(self):
        """Human-readable product type (for dashboard display)
        
        Must be statically implemented as a string"""
        raise NotImplementedError

    def get_full_reference(self, data=None):
        """Get the product full reference, including data
        
        Must return a string"""
        raise NotImplementedError

    def get_full_name(self, data=None):
        """Get the product full name, including data
        
        Must return a string"""
        raise NotImplementedError

    def get_price_per_item(self, data=None):
        """Returns the price of this product with the given data
        
        Must return a prices.Price object"""
        raise NotImplementedError

    def get_weight(self, data=None):
        """Weight of the product, for shipping

        Must returns an integer"""
        raise NotImplementedError

    def get_stock(self, data=None):
        """Stock for this product

        Must returns an integer"""
        raise NotImplementedError

    def too_few_in_stock(self, data=None):
        """Return True if this product should be restocked"""
        raise NotImplementedError

    def out_of_stock(self, data=None):
        """Return True if the product is out of stock
        
        (may be overriden)"""
        return self.get_stock(data) == 0

    def remove_from_stock(self, quantity):
        """Remove products from stock"""
        raise NotImplementedError

    @classmethod
    def remove_photos_from_disk(cls, sender, document, **kwargs):
        for p in document.photos:
            p.delete_files()



class Product(BaseProduct):
    human_type = lazy_gettext('Simple')
    purchasing_price = db.DecimalField(
                            db_field='pprice',
                            verbose_name=lazy_gettext('Purchasing price')
                            )
    gross_price = db.DecimalField(
                            db_field='gprice',
                            required=True,
                            verbose_name=lazy_gettext('Gross price')
                            )
    weight = db.IntField(default=0, verbose_name=lazy_gettext('Weight'))# grams
    stock = db.IntField(default=0, verbose_name=lazy_gettext('Stock'))
    stock_alert = db.IntField(
                        db_field='alert',
                        default=0,
                        verbose_name=lazy_gettext('Stock alert')
                        )

    def remove_from_stock(self, quantity):
        self.stock -= min(quantity, self.stock)

    def get_full_reference(self, data=None):
        return self.reference

    def get_full_name(self, data=None):
        return unicode(self)

    def get_price_per_item(self, data=None):
        gross = self.gross_price
        net = gross * ( 1 + self.tax.rate )
        return prices.Price(net, gross)

    def get_weight(self, data=None):
        return self.weight

    def get_stock(self, data=None):
        return self.stock

    def too_few_in_stock(self, data=None):
        return self.stock <= self.stock_alert and self.stock > 0

product_types = (
    ('simple', Product),
    )

type_to_product = {}
product_to_type = {}
for a, b in product_types:
    type_to_product[a] = b
    product_to_type[b] = a
