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

import copy
from decimal import Decimal

from mongoengine import signals
from prices import Price

from .. import app, db, get_locale
from ..mongo import TranslationsField


class UnavailableCarrier(Exception):
    pass


class Country(db.Document):
    code = db.StringField()
    default_name = db.StringField(db_field='d_name')
    name = TranslationsField()
    # The "carriers" entry is automatically updated by update_mapping below
    carriers = db.DictField()

    meta = {
        'ordering': ['code']
    }

    @property
    def prefixed_name(self):
        return u'{} - {}'.format(
                            self.code,
                            self.name.get(get_locale(), self.default_name)
                            )

    def get_shipping_price(self, carrier, weight):
        weights = self.carriers[str(carrier.id)]
        for w in weights:
            if w['weight'] > weight:
                return result_carrier_cost(Decimal(w['cost']))
        raise UnavailableCarrier


class CountriesGroup(db.Document):
    name = db.StringField()
    countries = db.ListField(db.ReferenceField(
                        Country,
                        reverse_delete_rule=db.DENY,
                        ))

    meta = {
        'ordering': ['name']
    }


class CarrierCosts(db.EmbeddedDocument):
    weight = db.IntField()
    # costs maps countries or groups ids to costs
    #
    # {
    #   '<country_or_group_id>': <price>,
    #   '<country_or_group_id>': <price>,
    #   'rest': <price>
    # }
    #
    # 'rest' is a special placeholder meaning "the rest of the world"
    costs = db.MapField(db.DecimalField())


class Carrier(db.Document):
    name = db.StringField()
    description = TranslationsField(db_field='desc')
    countries = db.ListField(db.ReferenceField(
                        Country,
                        reverse_delete_rule=db.DENY,
                        ))
    countries_groups = db.ListField(db.ReferenceField(
                                CountriesGroup,
                                reverse_delete_rule=db.DENY,
                                ), db_field='cgroups')
    tracking_url = db.StringField(db_field='tr_url')
    costs = db.SortedListField(db.EmbeddedDocumentField(CarrierCosts),
                               ordering='weight')

    @property
    def full_description(self):
        description = self.description.get(get_locale(), u'')
        return '{} ({})'.format(description, self.name)


def remove_null_costs(sender, document, **kwargs):
    costs = document.costs
    for entry in costs:
        if 'costs' in entry:
            for objectid, cost in entry['costs'].items():
                if cost is None:
                    entry['costs'].pop(objectid)
    document.costs = costs


def update_mapping(sender, document, **kwargs):
    # First, map countries IDs to carriers
    countries_carriers_mapping = {}
    rest = []
    for data in document.costs:
        weight = data['weight']
        for country, cost in data['costs'].iteritems():
            if country == 'rest':
                countries = 'rest'
            else:
                countries = []
                try:
                    countries = [Country.objects.get(id=country)]
                except Country.DoesNotExist:
                    try:
                        countries = CountriesGroup.objects.get(
                                                            id=country
                                                            ).countries
                    except:
                        pass
            result = {'weight': weight, 'cost': str(cost)}
            if countries == 'rest':
                rest.append(result)
            else:
                for c in countries:
                    countries_carriers_mapping.setdefault(c, []).append(result)

    docid = str(document.id)
    for country in Country.objects:
        costs = countries_carriers_mapping.get(country, rest)
        country.carriers[docid] = costs
        country.save()


def delete_mapping(sender, document, **kwargs):
    for country in Country.objects:
        country.carriers.pop(str(document.id), None)
        country.save()

signals.pre_save.connect(remove_null_costs, sender=Carrier)
signals.post_save.connect(update_mapping, sender=Carrier)
signals.pre_delete.connect(delete_mapping, sender=Carrier)

rounding = Decimal(str(app.config['SHIPPING_ROUNDING']))
multiplier = Decimal(str(app.config['SHIPPING_MULTIPLIER']))
preparation = Decimal(str(app.config['PACKAGE_PREPARATION_PRICE']))
tax = 1 + Decimal(str(app.config['SHIPPING_TAX']))/100


def result_carrier_cost(cost):
    """
    Add variable data to shipping costs

    Uses the following data from the configuration:

    * SHIPPING_MULTIPLIER: multiply the cost by this value before any other
                           calculation
    * PACKAGE_PREPARATION_PRICE: fixed price added to the shipping cost, no
                                 detail given to the customer
    * SHIPPING_ROUNDING: round the shipping price (always rounding up)
    * SHIPPING_TAX: tax added to the shipping price

    Returns a Price object
    """
    cost = Decimal(cost) * multiplier + preparation
    how_many_roundings = cost // rounding + 1
    cost = rounding * how_many_roundings
    return Price(cost*tax, cost)


def carriers_by_country_and_weight(country, weight):
    """
    Calculate and return all available carriers for a destination country and
    a specific weight

    The PACKAGE_WEIGHT configuration value will be added to the weight for
    each calculation
    """
    try:
        country = Country.objects.get(code=country)
    except Country.DoesNotExist:
        return []
    weight += app.config['PACKAGE_WEIGHT']
    resultcarriers = []
    for carrier, costs in country.carriers.iteritems():
        try:
            carrierobj = Carrier.objects.get(id=carrier)
        except Carrier.DoesNotExist:
            continue
        for cost in costs:
            if cost['weight'] >= weight:
                resultcarriers.append({
                                'carrier': carrierobj,
                                'cost': result_carrier_cost(cost['cost']).net
                                })
                break
    resultcarriers.sort(key=lambda carrier: carrier['cost'])
    return resultcarriers
