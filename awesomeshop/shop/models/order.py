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

from ... import app, db
from ...auth.models import User
from ...shipping.models import Carrier

from .product import Product



class OrderProduct(db.EmbeddedDocument):
    reference = db.StringField(db_field='ref')
    gross_price = db.StringField(db_field='gprice')
    net_price = db.StringField(db_field='nprice')
    line_gross_price = db.StringField(db_field='lgprice')
    line_net_price = db.StringField(db_field='lnprice')
    quantity = db.IntField(db_field='qty')
    product = db.ReferenceField(Product)
    name = db.StringField()
    qty_reduced_because_of_stock = db.BooleanField(db_field='insuff_stock')
    on_demand = db.BooleanField(db_field='dem')
    data = db.DictField()



class Order(db.Document):
    customer = db.ReferenceField(User, db_field='cust')
    status = db.StringField(db_field='stat')
    number = db.SequenceField(db_field='nb')
    number_prefix = db.StringField(db_field='nb_pfix',
                                   default=app.config['ORDER_PREFIX'])
    date = db.DateTimeField(default=datetime.datetime.now)
    invoice_number = db.IntField(db_field='inb')
    invoice_number_prefix = db.StringField(
                                    db_field='inb_pfix',
                                    default=app.config['INVOICE_PREFIX']
                                    )
    invoice_date = db.DateTimeField(db_field='idate')
    delivery = db.StringField()
    billing = db.StringField(db_field='bill')
    billing_firstname = db.StringField(db_field='bill_fn')
    billing_lastname = db.StringField(db_field='bill_ln')
    products = db.EmbeddedDocumentListField(OrderProduct)
    gross_subtotal = db.StringField(db_field='gsub')
    net_subtotal = db.StringField(db_field='nsub')
    carrier = db.ReferenceField(Carrier)
    carrier_description = db.StringField(db_field='car_desc')
    gross_shipping = db.StringField(db_field='gship')
    net_shipping = db.StringField(db_field='nship')
    gross_total = db.StringField(db_field='gtot')
    net_total = db.StringField(db_field='ntot')
    numeric_total = db.DecimalField(db_field='tot')
    payment_id = db.StringField(db_field='p_id')
    payment_description = db.StringField(db_field='p_desc')
    payment_data = db.DynamicField(db_field='p_data')
    payment_date = db.DateTimeField(db_field='p_date')
    payment_message = db.StringField(db_field='p_msg')
    accept_reused_package = db.BooleanField(db_field='reuse')
    shipping_date = db.DateTimeField(db_field='s_date')
    tracking_url = db.StringField(db_field='turl')
    tracking_number = db.StringField(db_field='tnum')
    on_demand = db.BooleanField(db_field='dem')
    on_demand_delay_min = db.IntField(db_field='dem_min')
    on_demand_delay_max = db.IntField(db_field='dem_max')

    meta = {
        'ordering': ['-number']
    }
