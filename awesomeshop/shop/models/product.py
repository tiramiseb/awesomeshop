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
# * signals must be added in .shop_signals, copying signals for Product

class BaseProduct(db.Document, StockedItem):
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

    def get_price_per_item(self):
        gross = self.gross_price
        net = gross * ( 1 + self.tax.rate )
        return prices.Price(net, gross)

    def get_stock(self):
        return self.stock

    @property
    def type(self):
        """Must be statically implemented as a string
        
        A corresponding entry must be added to the product_types dict"""
        raise NotImplementedError

    @property
    def purchasing_price(self):
        """Must be implemented as a Decimal"""
        raise NotImplementedError

    @property
    def gross_price(self):
        """Must be implemented as a Decimal"""
        raise NotImplementedError

    @property
    def weight(self):
        """Must be implemented as an integer"""
        raise NotImplementedError

    @property
    def stock(self):
        """Must be implemented as an integer"""
        raise NotImplementedError

    @property
    def stock_alert(self):
        """Must be implemented as an integer"""
        raise NotImplementedError

    @classmethod
    def remove_photos_from_disk(cls, sender, document, **kwargs):
        for p in document.photos:
            p.delete_files()



class Product(BaseProduct):
    type = lazy_gettext('Simple')
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


product_types = {
        'simple': Product
        }
