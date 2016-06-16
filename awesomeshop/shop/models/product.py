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
import random
import string
from decimal import Decimal

from mongoengine import signals
from satchless.item import StockedItem
import prices

from ... import app, db, get_locale
from ...mongo import TranslationsField
from ...photo import Photo
from ...page.models import Page
from .category import Category
from .tax import Tax


class BaseProduct(db.Document, StockedItem):
    """Base class for products: this one should not be used alone

    All methods (and properties) raising NotImplementedError must be
    implemented in the children classes.

    The data argument must be a dictionary, allowing variations to a product.

    When there is no data given to the methods, all products types must act
    as if they were regular products, without variations etc.

    External code must not call methods or attributes present only on one
    of the children classes.

    Whenever possible, methods in children classes should be private
    """
    created_at = db.DateTimeField(db_field='create',
                                  default=datetime.datetime.now)
    slug = db.StringField()
    reference = db.StringField(db_field='ref')
    category = db.ReferenceField(Category, db_field='cat',
                                 reverse_delete_rule=db.DENY)
    documentation = db.ReferenceField(
                            Page,
                            db_field='doc',
                            reverse_delete_rule=db.DENY
                            )
    keywords = db.StringField(db_field='kw')
    on_sale = db.BooleanField(db_field='sale')
    name = TranslationsField()
    description = TranslationsField(db_field='desc')
    related_products = db.ListField(
                            db.ReferenceField(
                                'self',
                                reverse_delete_rule=db.PULL
                                ),
                            db_field='rel',
                            )
    photos = db.EmbeddedDocumentListField(Photo)

    meta = {
            'collection': 'product',
            'allow_inheritance': True,
            'ordering': ['reference']
        }

    @property
    def type(self):
        raise NotImplementedError

    @property
    def path(self):
        return '{}/{}'.format(self.category.path, self.slug)

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
    def related_products_on_sale(self):
        return [p for p in self.related_products if p.on_sale]

    @property
    def main_photo(self):
        if self.photos:
            return self.photos[0]

    def get_price_per_item(self, data=None):
        """
        Return the price for the item, as a prices.Price object
        """
        raise NotImplementedError

    def get_weight(self, data=None):
        """
        Return the weight for the item, in grams
        """
        raise NotImplementedError

    def get_stock(self, data=None):
        """
        Return the stock for the item
        """
        raise NotImplementedError

    def get_delay(self, data=None):
        """
        Return the delay needed before shipping (preparation, etc), in days

        For immediate shipping, must return a minimal shipping delay
        (see app.config['SHIPPING_DELAY'])
        """
        raise NotImplementedError

    def get_overstock_delay(self, data=None):
        """
        Return the delay needed when the product is not immediately available
        (on demand...), in days

        When the product cannot be ordered without an immediate availability,
        must return -1
        """
        raise NotImplementedError

    def get_details(self, data=None):
        """
        Return details for the product (for instance, to be displayed in the
        cart page, to differentiate instanves with different data)
        """
        raise NotImplementedError

    def destock(self, quantity, data=None):
        """
        Remove product(s) from stock, when creating an order

        (this method must save the object)

        Return a tuple or a list:

        (
            <integer: quantity to be added to the order>,
            <integer: quantity directly taken from stock>,
            <integer: shipping delay, in days>
        )
        """
        raise NotImplementedError

    def restock(self, quantity, data=None):
        """
        Add product(s) tp stock, when cancelling an order

        (this method must save the object)
        """
        raise NotImplementedError


class RegularProduct(BaseProduct):
    type = 'regular'
    tax = db.ReferenceField(Tax, reverse_delete_rule=db.DENY)
    on_demand = db.BooleanField(db_field='dem')
    purchasing_price = db.DecimalField(db_field='pprice')
    gross_price = db.DecimalField(db_field='gprice')
    weight = db.IntField()
    stock = db.IntField()
    stock_alert = db.IntField(db_field='alert')

    @property
    def _net_price(self):
        return (self.gross_price * Decimal(1 + self.tax.rate)).quantize(
                                                                Decimal('1.00')
                                                                )

    def get_price_per_item(self, data=None):
        return prices.Price(self._net_price, self.gross_price)

    def get_weight(self, data=None):
        return self.weight

    def get_stock(self, data=None):
        return self.stock

    def get_delay(self, data=None):
        return app.config['SHIPPING_DELAY']

    def get_overstock_delay(self, data=None):
        if self.on_demand:
            return app.config['ON_DEMAND_DELAY']
        else:
            return -1

    def get_details(self, data=None):
        return None

    def destock(self, quantity, data=None):
        """Remove the given quantity or less if the stock is not enough"""
        if self.on_demand:
            if quantity > self.stock:
                from_stock = self.stock
                delay = app.config['ON_DEMAND_DELAY']
            else:
                from_stock = quantity
                delay = app.config['SHIPPING_DELAY']
        else:
            quantity = min(quantity, self.stock)
            from_stock = quantity
            delay = app.config['SHIPPING_DELAY']
        self.stock = self.stock - from_stock
        self.save()
        return (quantity, from_stock, delay)

    def restock(self, quantity, data=None):
        self.stock += quantity
        self.save()


class KitSubProductOption(db.EmbeddedDocument):
    quantity = db.IntField(db_field='qty')
    product = db.ReferenceField(BaseProduct)

    @property
    def selected_string(self):
        return '{}*{}'.format(self.quantity, self.product.id)
    
    def get_price(self):
        var = self._instance._instance.price_variation
        if self._instance._instance.euros_instead_of_percent:
            result = self.product.get_price_per_item() * self.quantity + var
        else:
            result = (
                        self.product.get_price_per_item() * self.quantity
                     ) * (
                        1 + var / 100
                     )
        return result

    def get_weight(self):
        return self.product.get_weight() * self.quantity

    def get_stock(self):
        return self.product.get_stock() / self.quantity

    def get_delay(self):
        return self.product.get_delay()

    def get_overstock_delay(self):
        return self.product.get_overstock_delay()

    def get_details(self):
        return {
                'name': self.product.name.get(get_locale(), u''),
                'quantity': self.quantity
                }

    def destock(self, quantity):
        quantity, from_stock, delay = self.product.destock(
                                                    quantity * self.quantity
                                                    )
        quantity = quantity / self.quantity
        from_stock = from_stock / self.quantity
        return (quantity, from_stock, delay)

    def restock(self, quantity):
        self.product.restock(quantity * self.quantity)


class DisabledFakeSubProductOption:

    def get_price(self):
        return prices.Price(0)

    def get_weight(self):
        return 0

    def get_stock(self):
        # Randomly chosen 2^32 :)
        return 4294967296

    def get_delay(self):
        return 0

    def get_overstock_delay(self):
        return 0

    def get_details(self):
        return None

    def destock(self, quantity):
        return (quantity, quantity, 0)

    def restock(self, quantity):
        pass


class KitSubProduct(db.EmbeddedDocument):
    id = db.StringField(default=lambda:
            ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
            )
    options = db.EmbeddedDocumentListField(KitSubProductOption)
    can_be_disabled = db.BooleanField(db_field='dis')
    default = db.StringField(db_field='dft')

    def get_selected_string(self, data):
        return data.get(self.id, self.default)

    def get_selected(self, data):
        selected = self.get_selected_string(data)
        default = DisabledFakeSubProductOption()
        for opt in self.options:
            if opt.selected_string == selected:
                return opt
            if opt.selected_string == self.default:
                default = opt
        # If this method has not returned yet, it means the requested
        # value is invalid, so the default option is used
        return default

    def get_price(self, data):
        return self.get_selected(data).get_price()

    def get_weight(self, data):
        return self.get_selected(data).get_weight()

    def get_stock(self, data):
        return self.get_selected(data).get_stock()

    def get_delay(self, data):
        return self.get_selected(data).get_delay()

    def get_overstock_delay(self, data):
        return self.get_selected(data).get_overstock_delay()

    def get_details(self, data):
        return self.get_selected(data).get_details()

    def destock(self, quantity, data):
        return self.get_selected(data).destock(quantity)

    def restock(self, quantity, data):
        self.get_selected(data).restock(quantity)


class KitProduct(BaseProduct):
    type = 'kit'
    products = db.EmbeddedDocumentListField(KitSubProduct)
    tax = db.ReferenceField(Tax, reverse_delete_rule=db.DENY)
    price_variation = db.DecimalField(db_field='var', default=0)
    euros_instead_of_percent = db.BooleanField(db_field='euro', default=False)

    def get_price_per_item(self, data={}):
        price = prices.Price(0)
        for prod in self.products:
            price += prod.get_price(data)
        return price

    def get_weight(self, data={}):
        return sum(prod.get_weight(data) for prod in self.products)

    def get_stock(self, data={}):
        return min(prod.get_stock(data) for prod in self.products)

    def get_delay(self, data={}):
        return max(prod.get_delay(data) for prod in self.products)

    def get_details(self, data={}):
        details = []
        for prod in self.products:
            this_detail = prod.get_details(data)
            if this_detail:
                details.append(this_detail)
        return details

    def get_overstock_delay(self, data={}):
        delays = []
        for prod in self.products:
            this_delay = prod.get_overstock_delay(data)
            # If one option is unavailable overstock,
            # this kit is unavailable overstock too
            if this_delay == -1:
                return -1
            else:
                delays.append(this_delay)
        return max(delays)

    def destock(self, quantity, data={}):
        # TODO Be more precise on destocking so restocking would be correct
        quantities = []
        from_stock_s = []
        delays = []
        for prod in self.products:
            quantity, from_stock, delay = prod.destock(quantity, data)
            quantities.append(quantity)
            from_stock_s.append(from_stock)
            delays.append(delay)
        return (max(quantities), max(from_stock_s), max(delays))

    def restock(self, quantity, data={}):
        for prod in self.products:
            prod.restock(quantity, data)


def check_defaults(sender, document, **kwargs):
    """For kit products, if no default option is set, select the first one"""
    for product in document.products:
        possible_options = ['{}*{}'.format(o.quantity, o.product.id)
                            for o in product.options]
        if product.can_be_disabled:
            possible_options.append('none')
        if product.default not in possible_options:
            product.default = possible_options[0]


def update_search(sender, document, **kwargs):
    from ...search import index_product
    index_product(document)


def forbid_if_used_in_kit_and_delete_search(sender, document, **kwargs):
    # TODO Forbid deleting product if used in a kit product
    from ...search import delete_product
    delete_product(document)


signals.pre_save.connect(check_defaults, sender=KitProduct)
signals.post_save.connect(update_search, sender=BaseProduct)
signals.pre_delete.connect(forbid_if_used_in_kit_and_delete_search,
                           sender=BaseProduct)

products = {
        'regular': RegularProduct,
        'kit': KitProduct
        }
