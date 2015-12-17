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

from flask_restful import Resource

from .. import rest
from .cart import Cart

class SessionCart(Resource):
    def get(self):
        cart_modified_because_of_stock = False
        cart = Cart.from_session()
        # Verify quantities
        for line in cart:
            if not line.product.on_demand:
                if line.quantity > line.get_stock():
                    cart_modified_because_of_stock = True
                    cart.add(line.product, line.get_stock(), replace=True)
        ret = cart.as_dict()
        ret['modified'] = cart_modified_because_of_stock
        ret['on_demand'] = cart.stock_status == 'on_demand'
        return ret
rest.add_resource(SessionCart, '/api/cart')

