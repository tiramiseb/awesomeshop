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

from flask import abort, request, redirect, url_for
from flask.ext.babel import _, lazy_gettext
from flask.ext.login import current_user
import payplug

from ... import app
from ...helpers import render_front, login_required
from ...shop.models import Order

@app.route('/orders/<order_number>/payplug_return')
@login_required
def payplug_return(order_number):
    order = Order.objects.get_or_404(number=order_number,
                                     customer=current_user.to_dbref())
    if order.status == 'awaiting_payment' and order.payment_data:
        order.set_status('awaiting_provider')
        order.save()
    return redirect(url_for('order', order_number=order_number))

@app.route('/orders/<order_number>/payplug_cancel')
@login_required
def payplug_cancel(order_number):
    order = Order.objects.get_or_404(number=order_number,
                                     customer=current_user.to_dbref())
    order.payment_data = None
    order.save()
    return render_front('payment/payplug_cancel.html', order=order)

@app.route('/orders/<order_number>/payplug_ipn', methods=['POST'])
def payplug_ipn(order_number):
    order = Order.objects.get_or_404(number=order_number)
    resource = payplug.notifications.treat(request.data)
    if resource.object == 'payment' and \
            resource.metadata['order_number'] == order.number and \
            resource.metadata['invoice_number'] == order.invoice_number:
        if resource.is_paid:
            order.set_status('payment_received')
        elif resource.failure:
            code = resource.failure.code
            if code == 'processing_error':
                message = _('Error while processing the card')
            elif code == 'card_declined':
                message = _('Your bank declined the payment')
            elif code == 'insufficient_funds':
                message = _('Insufficient funds on your bank account')
            elif code == '3ds_declined':
                message = _('3-D secure protection has failed')
            elif code == 'incorrect_number':
                message = _('The card number is incorrect')
            elif code == 'fraud_suspected':
                message = _('A potential fraud has been detected')
            elif code == 'aborted':
                message = _('Payment has been aborted')
            else:
                message = _('Unknown problem')
            order.payment_message = message
            order.payment_data = None
            order.set_status('payment_failed')
        order.save()
        return ''
    abort(403)

