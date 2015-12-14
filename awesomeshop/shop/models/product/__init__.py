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

from .core import BaseProduct, product_types, type_to_product, product_to_type
from .product import Product
# This one will be imported later. Committed too soon
#from .modularproduct import ModularProduct

# When adding a new product type:
#
# * it must inherit from core.BaseProduct
# * all functions raising NotImplementedError must be overriden
# * a new entry must be added to the .core.product_types dict

for a, b in product_types:
    type_to_product[a] = b
    product_to_type[b] = a
