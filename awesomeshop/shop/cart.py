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

from flask import session
from flask.ext.babel import lazy_gettext
from satchless import cart

from .. import app
from .models import BaseProduct

stock_messages = {
        'in_stock': '<span class="text-success">{}</span>'.format(
                lazy_gettext('In stock')
                ),
        'out_of_stock': '<span class="text-danger">{}</span>'.format(
                lazy_gettext('Out of stock')
                ),
        'insufficient_stock': '<span class="text-danger">{}</span>'.format(
                lazy_gettext('Insufficient stock')
                ),
        'on_demand': '<span class="text-info">{}</span>'.format(
                lazy_gettext(
                    'Delay %(min)d-%(max)d days',
                    min=app.config['ON_DEMAND_DELAY_MIN'],
                    max=app.config['ON_DEMAND_DELAY_MAX']
                    )
                )
        }
class CartLine(cart.CartLine):

    @property
    def weight(self):
        return self.product.weight * self.quantity

    @property
    def stock_status(self):
        if self.quantity <= self.product.stock:
            return 'in_stock'
        if self.product.on_demand:
            return 'on_demand'
        if self.product.stock > 0:
            return 'insufficient_stock'
        return 'out_of_stock'

    @property
    def stock_message(self):
        return stock_messages[self.stock_status]

    def for_session(self):
        """Export data for session storage"""
        return {
            'product_id': str(self.product.id),
            'quantity': self.quantity
        }

    @classmethod
    def from_session(cls, session_data):
        """Create cart from session data"""
        product = BaseProduct.objects.get(id=session_data['product_id'])
        quantity = session_data['quantity']
        return cls(product, quantity)

class Cart(cart.Cart):

    def create_line(self, product, quantity, data):
        return CartLine(product, quantity, data)

    def quantity(self, product=None):
        """Return the quantity of products

        If "product" is None, returns total quantity of the cart
        If "product" is not none, returns total quantity for the product
        """
        if product:
            line = self.get_line(product)
            if line:
                return line.quantity
            return 0
        else:
            return sum(line.quantity for line in self)

    def weight(self, product=None):
        """Return the products weight

        If "product" is None, returns total weight of the cart
        If "product" is not none, returns total weight for the product
        """
        if product:
            line = self.get_line(product)
            if line:
                return line.weight
            return 0
        else:
            return sum(line.weight for line in self)

    @property
    def stock_status(self):
        all_stocks = [l.stock_status for l in self]
        if 'out_of_stock' in all_stocks:
            return 'out_of_stock'
        if 'insufficient_stock' in all_stocks:
            return 'insufficient_stock'
        if 'on_demand' in all_stocks:
            return 'on_demand'
        return 'in_stock'

    @property
    def stock_message(self):
        return stock_messages[self.stock_status]

    @property
    def must_recalc(self):
        return self.stock_status in ('out_of_stock', 'insufficient_stock')

    # Session storage
    def to_session(self):
        """Export data for session storage"""
        session['cart'] = [ line.for_session() for line in self ]

    @classmethod
    def from_session(cls):
        """Create cart from session data"""
        cart = cls()
        if 'cart' in session:
            for line in session.get('cart'):
                try:
                    cart._state.append(CartLine.from_session(line))
                except BaseProduct.DoesNotExist:
                    pass
        return cart

    def add(self, product, quantity, replace=False):
        # If the product allows "on demand" orders, do not check the quantity
        cart.Cart.add(self, product, quantity, replace=replace,
                      check_quantity = not product.on_demand)
        self.to_session()
