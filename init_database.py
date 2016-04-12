#!/usr/bin/env python
# -*- coding: utf8 -*-

# Copyright 2015-2016 Sébastien Maccagnoni-Munch
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

# Flush and initialize the MongoDB database with basic data

import sys

from mongoengine.connection import get_db

from awesomeshop import db, shipping
from awesomeshop.auth.models import Address, User
from awesomeshop.page.models import Page
from awesomeshop.shipping import init as shipping_init
from awesomeshop.shipping.models import Country, CountriesGroup, Carrier
from awesomeshop.shop.models import Tax, Category, Product, Url, Order

sure = raw_input('WARNING! THE DATABASE WILL BE EMPTIED! ARE YOU SURE [yn]? ')

if sure not in ('y', 'Y', 'yes'):
    sys.exit(1)

print '* Deleting previous data'
Address.drop_collection()
User.drop_collection()
Carrier.drop_collection()
CountriesGroup.drop_collection()
Country.drop_collection()
Url.drop_collection()
Product.drop_collection()
Category.drop_collection()
Tax.drop_collection()
Page.drop_collection()
Order.drop_collection()
get_db().drop_collection('mongoengine.counters')

print '* Creating an administrator (admin@example.com/admin)'
admin = User(email='admin@example.com')
admin.set_password('admin')
admin.is_admin = True
admin.save()

print '* Creating countries'
shipping_init.create_countries_from_restcountries()
shipping_init.create_legal_groups()
