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

import datetime

from .helpers import Setting
from .shop.models import BaseProduct, Order
from .shop.models import Url

###############################################################################
# Functions used to upgrade the database content
#
# These functions must not modify content which is already correct (so that it
# doesn't break if someone runs the upgrade functions on an already-upgraded
# database)

def add_product_cls():
    products = BaseProduct._get_collection()
    products.update_many({'_cls': None}, {'$set': {'_cls': 'BaseProduct.Product'}})
    urls = Url._get_collection()
    urls.update_many(
            {'doc._cls': 'Product'},
            {'$set':{'doc._cls': 'BaseProduct.Product'}}
            )

def add_ondemand():
    products = BaseProduct._get_collection()
    products.update_many({'dem': None}, {'$set': {'dem': False}})

def add_creationdate():
    old_date = datetime.datetime(1970, 1, 1)
    products = BaseProduct._get_collection()
    products.update_many({'create': None}, {'$set': {'create': old_date}})

###############################################################################
# Ordered list of all upgrade functions
upgrades = [
    add_product_cls,
    add_ondemand,
    add_creationdate
    ]

def upgrade():
    latest = len(upgrades)
    try:
        version = Setting.objects.get(name='db_upgrade_version')
    except:
        version = Setting(name='db_upgrade_version', value=0)
    if version.value < latest:
        print 'Upgrading from version {} to {}'.format(version.value, latest)
        for fct in upgrades[version.value:]:
            fct()
        version.value = latest
        version.save()
