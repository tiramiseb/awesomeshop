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
from flask.ext.babel import lazy_gettext

from .... import db
from ....mongo import model_form
from .core import BaseProduct, product_types

class Product(BaseProduct):
    """Basic products, with no option and no variants"""
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

    def add_to_stock(self, quantity, data=None):
        self.stock += min(quantity, self.stock)

    def remove_from_stock(self, quantity, data=None):
        self.stock -= min(quantity, self.stock)

    def get_full_reference(self, data=None):
        return self.reference

    def get_full_name(self, data=None):
        return self.loc_name

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

    def get_form(self, formdata):
        return ProductForm(formdata, self)

ProductForm = model_form(Product)

product_types.append(('simple', Product))
