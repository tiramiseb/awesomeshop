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
import re

from . import app, db
from .helpers import Setting
from .page.models import Page
from .shipping.models import Carrier
from .shop.models.order import Order
from .shop.models.product import BaseProduct

class Counters(db.Document):
    """Simulate counters as a MongoEngine class so that we can access it..."""
    meta = {
            'collection': 'mongoengine.counters'
            }

###############################################################################
# Functions used to upgrade the database content
#
# These functions must not modify content which is already correct (so that it
# doesn't break if someone runs the upgrade functions on an already-upgraded
# database)


def add_product_cls():
    pass
    # Deprecated because it has been reverted
    # products = BaseProduct._get_collection()
    # products.update_many({'_cls': None},
    #                      {'$set': {'_cls': 'BaseProduct.Product'}})
    # urls = Url._get_collection()
    # urls.update_many(
    #         {'doc._cls': 'Product'},
    #         {'$set':{'doc._cls': 'BaseProduct.Product'}}
    #         )


def add_ondemand():
    products = BaseProduct._get_collection()
    products.update_many({'dem': None}, {'$set': {'dem': False}})


def add_creationdate():
    old_date = datetime.datetime(1970, 1, 1)
    products = BaseProduct._get_collection()
    products.update_many({'create': None}, {'$set': {'create': old_date}})


def merge_weights_and_costs():
    # Old format:
    #
    # weights: list of weights (integers)
    # costs : list of dicts associating countries IDs (strings) or
    #         countriesgroups IDs (strings)
    #         to dicts associating weights (strings) with costs (floats)
    #
    # New format:
    #
    # weights: list of lists, in which the first field is the weight (integer)
    #          and the second field is a dict associating countries IDs
    #          (strings) or countriesgroups IDs (strings) to costs (floats)
    carriers = Carrier._get_collection()
    for carrier in carriers.find(projection=('weights', 'costs')):
        if 'weights' in carrier:
            # If "weights" does not exist in the object, then it already used
            # the new format
            old_weights = carrier['weights']
            old_weights.sort()
            new_weights = {}
            for weight in old_weights:
                new_weights[unicode(weight)] = {}
            for country, costs in carrier['costs'].iteritems():
                for weight, cost in costs.iteritems():
                    if weight in new_weights:
                        # Lose data if the weight is not defined
                        new_weights[weight][country] = cost
            new_costs_as_list = []
            for weight in old_weights:
                new_costs_as_list.append({
                            'weight': weight,
                            'costs': new_weights[unicode(weight)]
                            })
            carriers.update_one(
                    {'_id': carrier['_id']},
                    {
                        '$set': {'costs': new_costs_as_list},
                        '$unset': {'weights': ''}
                        }
                    )


def reunite_products():
    # Deprecated again, products inheritance is used again
    # products = Product._get_collection()
    # products.update_many({},
    #                     {'$unset': {'_cls': ''}})
    pass
    # Url documents don't exist anymore, cannot get their collection
    # urls = Url._get_collection()
    # urls.update_many(
    #         {'doc._cls': 'BaseProduct.Product'},
    #         {'$set': {'doc._cls': 'Product'}}
    #         )


def remove_insuff_stock_from_orders():
    orders = Order._get_collection()
    for o in orders.find():
        newproducts = o['products'][:]
        for p in newproducts:
            if 'insuff_stock' in p:
                p.pop('insuff_stock')
        orders.find_one_and_update(
                    {'_id': o['_id']},
                    {'$set': {'products': newproducts}}
                    )


def change_payment_description():
    orders = Order._get_collection()
    for o in orders.find({'p_desc': {'$regex': '^<i class'}}):
        m = re.match('<i class="fa fa-(.*)"></i> (.*)', o['p_desc'])
        orders.find_one_and_update(
                {'_id': o['_id']},
                {'$set': {'p_ico': m.group(1), 'p_desc': m.group(2)}}
                )


def readd_product_cls():
    # Enable subproducts again...
    # It was not a bad idea after all, but it may have been too soon...
    products = BaseProduct._get_collection()
    products.update_many({'_cls': None},
                         {'$set': {'_cls': 'BaseProduct.RegularProduct'}})


def on_demand_to_delay():
    orders = Order._get_collection()
    for o in orders.find():
        on_demand = o.get('dem', None)
        order_delay = o.get('dem_max', app.config['ON_DEMAND_DELAY'])
        shipping_delay = app.config['SHIPPING_DELAY']
        for p in o['products']:
            dem = p.get('dem', None)
            if dem is True:
                p['delay'] = order_delay
            else:
                p['delay'] = shipping_delay
            p.pop('dem', None)
        if on_demand is True:
            orders.find_one_and_update(
                    {'_id': o['_id']},
                    {
                        '$set': {
                            'delay': order_delay,
                            'products': o['products']
                            },
                        '$unset': {
                            'dem': '',
                            'dem_min': '',
                            'dem_max': ''
                            }
                        }
                    )
        elif on_demand is False:
            orders.find_one_and_update(
                    {'_id': o['_id']},
                    {
                        '$set': {
                            'delay': shipping_delay,
                            'products': o['products']
                            },
                        '$unset': {
                            'dem': '',
                            'dem_min': '',
                            'dem_max': ''
                            }
                        }
                    )

def remove_page_rank():
    pages = Page._get_collection()
    pages.update_many({}, {'$unset': {'rank': ''}})
    counters = Counters._get_collection()
    counters.delete_one({'_id': 'page.rank'})

def remove_payment_description():
    orders = Order._get_collection()
    orders.update_many({}, {'$unset': {'p_desc': ''}})

###############################################################################
# Ordered list of all upgrade functions
upgrades = [
    (add_product_cls, '2015: allow subproducts (deprecated)'),
    (add_ondemand, '2015: allow "on demand" products'),
    (add_creationdate, '2015: add creation date to products'),
    (
        merge_weights_and_costs,
        '18/01/2016: change how weights and costs are stored'
        ),
    (reunite_products, '09/02/2016: cancel the subproducts feature'),
    (
        remove_insuff_stock_from_orders,
        '16/04/2016: remove the "insufficient stock" info from orders'
        ),
    (
        change_payment_description,
        '16/04/2016: split the payment description and its icon'
        ),
    (readd_product_cls, '22/04/2016: allow subproducts again'),
    (on_demand_to_delay, '03/05/2016: store delays instead of on_demand'),
    (
        remove_page_rank,
        '28/08/2016: remove page rank, they are now ordered alphabetically'
        ),
    (
        remove_payment_description,
        '03/09/2016: remove static payment description in orders'
        )
    ]


def upgrade():
    latest = len(upgrades)
    try:
        version = Setting.objects.get(name='db_upgrade_version')
    except:
        version = Setting(name='db_upgrade_version', value=0)
    if version.value < latest:
        print 'Upgrading database from version {} to version {}...'.format(
                                                                version.value,
                                                                latest
                                                                )
        for fct, desc in upgrades[version.value:]:
            print '>', desc
            fct()
        version.value = latest
        version.save()
        print 'Done upgrading!'
