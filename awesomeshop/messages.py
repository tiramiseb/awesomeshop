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

from flask_babel import _

def messages():
    return {
        # Pages titles
        'Addresses': _('Addresses'),
        'Category': _('Category'),
        'Documentation': _('Documentation'),
        'Home': _('Home'),
        'Information': _('Information'),
        'My cart': _('Mon panier'),
        'New products': _('New products'),
        'Product': _('Product'),
        'Profile': _('Profile'),
        'Saved carts': _('Saved carts')
    }

