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

from flask_babel import _, lazy_gettext

from .. import app
from .base import PaymentMode


class SepaTransfer(PaymentMode):
    id = 'sepa_transfer'
    icon = 'exchange'
    description = lazy_gettext('SEPA bank transfer')

    def trigger(self, order):
        titles = [
            _('Recipient account owner'),
            _('Recipient account BIC'),
            _('Recipient account IBAN'),
            _('Transfer amount'),
            _('Transfer information')
            ]
        values = [
            app.config['SEPA_TRANSFER_RECIPIENT'],
            app.config['SEPA_TRANSFER_BIC'],
            app.config['SEPA_TRANSFER_IBAN'] + '          ',
            order.net_total,
            order.invoice_full_number
            ]
        lent = max([len(i) for i in titles])
        lenv = max([len(i) for i in values])
        line = '+-' + '-'*lent + '-+-' + '-'*lenv + '-+'
        message = [
            _('Please execute a SEPA bank transfer within %(num)d days '
              'with the following criteria:', num=app.config['PAYMENT_DELAY']),
            '',
            line,
            ]
        for i in range(0, 5):
            message.append(
                '| ' + titles[i] + (lent-len(titles[i]))*' ' + ' | ' +
                values[i] + (lenv-len(values[i]))*' ' + ' |'
                )
            message.append(line)

        return {
            'type': 'message',
            'message': '\n'.join(message)
            }
