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

from flask import abort


class PaymentMode:
    # Payment mode unique identifier (dev-understandable text)
    id = ''
    # Icon identifier from Font Awesome for this payment mode
    icon = ''
    # Human-understandable payment mode name/description
    description = ''

    def trigger(self, order):
        """
        Trigger the payment

        Arguments:

        * order: the order object

        Return value: a dictionary with the following content:

        * if the only action is displaying a message

        {
            'type': 'message',
            'message': '<the message to be displayed to the user, in reST>'
        }
        """
        abort(500)
