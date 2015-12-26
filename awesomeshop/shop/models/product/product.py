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

import prices

from .... import db
from .core import BaseProduct

class Product(BaseProduct):
    """Basic products, with no option and no variants"""
    purchasing_price = db.DecimalField(db_field='pprice')
    gross_price = db.DecimalField(db_field='gprice')
    weight = db.IntField()
    stock = db.IntField()
    stock_alert = db.IntField(db_field='alert')

    def get_full_name(self, data=None):
        return self.loc_name

    def get_price_per_item(self, data=None):
        gross = self.gross_price
        net = gross * ( 1 + self.tax.rate )
        return prices.Price(net, gross)
