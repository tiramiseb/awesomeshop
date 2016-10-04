# -*- coding: utf8 -*-

# Copyright 2016 Sébastien Maccagnoni-Munch
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

import os.path

from flask import abort, redirect, request, url_for
from flask_login import current_user
import payplug

from .. import app, login_required
from .base import PaymentMode


class PayPlug(PaymentMode):
    id = 'payplug'
    icon = 'credit-card'

    def __init__(self):
        payplug.set_secret_key(app.config['PAYPLUG_API_KEY'])

    def trigger(self, order):
        if order.status == 'awaiting_payment' and order.payment_data:
            payment = payplug.Payment.retrieve(order.payment_data)
        else:
            payment_data = {
                'amount': int(order.net_total * 100),
                'currency': 'EUR',
                'customer': {
                    'email': current_user.email,
                    'first_name': order.billing_firstname,
                    'last_name': order.billing_lastname
                    },
                'hosted_payment': {
                    'return_url': url_for('payplug_return',
                                          order_number=order.number,
                                          _external=True),
                    'cancel_url': url_for('payplug_cancel',
                                          order_number=order.number,
                                          _external=True),
                },
                'notification_url': url_for('payplug_ipn',
                                            order_number=order.number,
                                            _external=True),
                'metadata': {
                    'order_number': order.number,
                    'invoice_number': order.invoice_number
                },
            }
            payment = payplug.Payment.create(**payment_data)
            order.payment_data = payment.id
            order.save()
        return {
                'type': 'redirect',
                'target': payment.hosted_payment.payment_url
                }


@app.route('/payplug/return/<order_number>')
@login_required
def payplug_return(order_number):
    from ..shop.models.order import Order
    order = Order.objects.get_or_404(number=order_number,
                                     customer=current_user.to_dbref())
    if order.status == 'awaiting_payment' and order.payment_data:
        order.set_status('awaiting_provider')
        order.save()
    return redirect(os.path.join(request.url_root, 'orders',
                                 unicode(order_number)))


@app.route('/payplug/cancel/<order_number>')
@login_required
def payplug_cancel(order_number):
    from ..shop.models.order import Order
    order = Order.objects.get_or_404(number=order_number,
                                     customer=current_user.to_dbref())
    order.payment_data = None
    order.save()
    return redirect(os.path.join(request.url_root, 'orders',
                                 unicode(order_number)))


@app.route('/payplug/ipn/<order_number>', methods=['POST'])
def payplug_ipn(order_number):
    from ..shop.models.order import Order
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
                message = 'Error while processing the card'
            elif code == 'card_declined':
                message = 'Your bank declined the payment'
            elif code == 'insufficient_funds':
                message = 'Insufficient funds on your bank account'
            elif code == '3ds_declined':
                message = '3-D secure protection has failed'
            elif code == 'incorrect_number':
                message = 'The card number is incorrect'
            elif code == 'fraud_suspected':
                message = 'A potential fraud has been detected'
            elif code == 'aborted':
                message = 'Payment has been aborted'
            else:
                message = 'Unknown problem'
            order.payment_message = message
            order.payment_data = None
            order.set_status('payment_failed')
        order.save()
        return u''
    abort(403)
