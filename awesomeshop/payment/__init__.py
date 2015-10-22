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

from .mode import PaymentMode
from .payplug_awesomeshop import PayPlug

class SepaTransfer(PaymentMode):
    id = 'sepa_transfer'
    replay_button_text = lazy_gettext(
                            'See SEPA bank transfer information again'
                            )

    @property
    def text(self):
        return u'<i class="fa fa-exchange"></i> {}'.format(
                    _('SEPA bank transfer')
                    )

    def execute(self, order):
        return redirect(url_for('sepa_bank_transfer',
                                order_number=order.number))


modes = [
    PayPlug(),
    SepaTransfer()
    ]
