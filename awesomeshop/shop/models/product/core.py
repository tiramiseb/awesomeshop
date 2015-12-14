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
from flask.ext.babel import lazy_gettext
from satchless.item import StockedItem

from .... import db, get_locale
from ....mongo import TranslationsField
from ....photo import Photo
from ....page.models import Page
from ..category import Category
from ..tax import Tax


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
                        verbose_name=lazy_gettext('On demand if out of stock')
                        )
    meta = {
        'collection': 'product',
        'ordering': ['reference'],
        'allow_inheritance': True
    }

    @property
    def loc_name(self):
        return self.name.get(get_locale(), u'')

    def get_description(self, initial_header_level=3):
        parts = docutils.core.publish_parts(
                    source=self.description.get(get_locale(), u''),
                    settings_overrides = {
                        'initial_header_level': initial_header_level
                        },
                    writer_name='html')
        return parts['body']

    def get_documentation(self, initial_header_level=3):
        return self.documentation.get_text(initial_header_level)

    @property
    def url(self):
        from ..url import Url
        return Url.objects(document=self).only('url').first().url

    @property
    def type(self):
        return product_to_type[self.__class__]

    @property
    def list_icon(self):
        from ....rendering import render_front
        return render_front('shop/producticon/{}.html'.format(self.type),
                            product=self)

    def out_of_stock(self, data=None):
        """Return True if the product is out of stock
        
        (may be overriden)"""
        return self.get_stock(data) == 0

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

    def add_to_stock(self, quantity, data=None):
        """Add products to stock"""
        raise NotImplementedError

    def remove_from_stock(self, quantity, data=None):
        """Remove products from stock"""
        raise NotImplementedError

    def get_form(self, formdata):
        """Return a form specific to this product type
        (see ....mongo.model_form)"""
        # return SomeProductForm(formdata, self)
        raise NotImplementedError

    @classmethod
    def remove_photos_from_disk(cls, sender, document, **kwargs):
        for p in document.photos:
            p.delete_files()

product_types = []
type_to_product = {}
product_to_type = {}
