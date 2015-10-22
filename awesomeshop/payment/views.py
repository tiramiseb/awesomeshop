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

from flask.ext.login import current_user

from .. import app
from ..helpers import render_front, login_required
from ..shop.models import Order
from .payplug_awesomeshop import views

@app.route('/orders/<order_number>/sepa_bank_transfer')
@login_required
def sepa_bank_transfer(order_number):
    order = Order.objects.get_or_404(number=order_number,
                                     customer=current_user.to_dbref())
    return render_front('payment/sepa_bank_transfer.html', order=order)

