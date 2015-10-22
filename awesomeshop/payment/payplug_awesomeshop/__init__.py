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

from flask import redirect, url_for
from flask.ext.babel import _, lazy_gettext
from flask.ext.login import current_user
import payplug

from ... import app
from ..mode import PaymentMode

class PayPlug(PaymentMode):
    id = 'payplug'
    replay_button_text = lazy_gettext('Return to the payment page')

    def __init__(self):
        payplug.set_secret_key(app.config['PAYPLUG_API_KEY'])

    @property
    def text(self):
        return u'<i class="fa fa-credit-card"></i> {}'.format(
                    _('Credit card (secured by PayPlug)')
                    )

    def execute(self, order):
        if order.status == 'awaiting_payment' and order.payment_data:
            payment = payplug.Payment.retrieve(order.payment_data)
        else:
            payment_data = {
                'amount': int(order.numeric_total * 100),
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
        return redirect(payment.hosted_payment.payment_url)

