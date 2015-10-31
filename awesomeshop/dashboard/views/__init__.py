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

from ... import app
from ...rendering import admin_required, render_template
from ...shop.models import Order, Product

# Load other views when running the app
from . import carrier
from . import category
from . import country
from . import order
from . import page
from . import product
from . import tax
from . import user

@app.route('/dashboard')
@app.route('/dashboard/')
@admin_required
def dashboard():
    paid_orders = Order.objects(status='payment_received').order_by('number')
    prep_orders = Order.objects(status='preparation').order_by('number')
    awaiting_payment_orders = Order.objects(status='awaiting_payment').order_by('number')
    out_of_stock_products = BaseProduct.objects(stock=0)
    stock_alert_products = [BaseProduct.objects.get(id=i['_id']) for i in \
            BaseProduct.objects.aggregate(
                {'$project': {
                    'below_alert': {'$lte': ['$stock', '$alert']},
                    'stock': True
                    }
                },
                {'$match':{'below_alert': True, 'stock': {'$gt': 0}}}
                )]
    return render_template('dashboard/home.html', paid_orders=paid_orders,
                           prep_orders=prep_orders,
                           awaiting_payment_orders=awaiting_payment_orders,
                           out_of_stock_products=out_of_stock_products,
                           stock_alert_products=stock_alert_products)
