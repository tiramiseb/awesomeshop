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

from decimal import Decimal

from flask.ext.babel import lazy_gettext
from mongoengine import signals
import prices

from .. import app, db, get_locale
from ..mongo import TranslationsField

class Country(db.Document):
    code = db.StringField(required=True, max_length=10,
                          verbose_name=lazy_gettext('Code'))
    default_name = db.StringField(db_field='d_name', max_length=100,
                                  verbose_name=lazy_gettext('Default name'))
    name = TranslationsField(max_length=100)

    meta = {
        'ordering': ['code']
    }

    def __unicode__(self):
        return u'{} - {}'.format(self.code,
                                self.name.get(get_locale(), self.default_name))


class CountriesGroup(db.Document):
    name = db.StringField(max_length=50, verbose_name=lazy_gettext('Name'))
    countries = db.ListField(db.ReferenceField(
                        Country,
                        reverse_delete_rule=db.DENY,
                        verbose_name=lazy_gettext('Countries')
                        ))

    meta = {
        'ordering': ['name']
    }

    def __unicode__(self):
        return self.name

rounding = Decimal(str(app.config['SHIPPING_ROUNDING']))
multiplier = Decimal(str(app.config['SHIPPING_MULTIPLIER']))
preparation = Decimal(str(app.config['PACKAGE_PREPARATION_PRICE']))
tax = 1 + Decimal(str(app.config['SHIPPING_TAX']))/100
quantizer = Decimal('0.01')
class Carrier(db.Document):
    name = db.StringField(required=True, max_length=50,
                          verbose_name=lazy_gettext('Name'))
    description = TranslationsField(db_field='desc', max_length=100,
                                    verbose_name=lazy_gettext('Description'))
    countries = db.ListField(db.ReferenceField(
                        Country,
                        reverse_delete_rule=db.DENY,
                        verbose_name=lazy_gettext('Countries')
                        ))
    countries_groups = db.ListField(db.ReferenceField(
                                CountriesGroup,
                                reverse_delete_rule=db.DENY,
                                verbose_name=lazy_gettext('Countries groups')
                                ), db_field='cgroups')
    weights = db.SortedListField(db.IntField(choices=None),
                                 verbose_name=lazy_gettext('Weights'))
    tracking_url = db.StringField(
                        db_field='tr_url',
                        max_length=250,
                        verbose_name=lazy_gettext('Tracking URL (if any) - use "@" in place of the number')
                        )
    costs = db.DictField()

    meta = {
        'ordering': ['name']
    }

    def __unicode__(self):
        return u'{} ({})'.format(self.description.get(get_locale(), u''),
                                 self.name)

    def get_price(self, country_or_group, weight, which=None, exact=False):
        """Get the price for the association of a country and a weight

        country_or_group = "rest" for the rest of the world

        which:
        * 'purchasing' : the price we pay
        * 'gross' : the gross price anounced to the customers
        * 'net' : the net price paid by the customers
        * None (default) : a dict with all three

        exact: exact price (for dashboard), or the price immediately greater
               (for shipping calculation)
        """
        c_or_g = self.costs.get(unicode(country_or_group))
        if c_or_g:
            # Get the price for the weight that is equal or
            # immediately greater to the requested weight
            for w in sorted([int(i) for i in c_or_g.keys()]):
                if (exact and w == weight) or (not exact and w >= weight):
                    purchasing = Decimal(c_or_g[str(w)])
                    if which == 'purchasing':
                        return purchasing.quantize(quantizer)
                    net = (purchasing * multiplier + preparation) * tax
                    how_many_roundings = net // rounding + 1
                    net = rounding * how_many_roundings
                    if which == 'net':
                        return net.quantize(quantizer)
                    gross = net / tax
                    if which == 'gross':
                        return gross.quantize(quantizer)
                    return {
                        'purchasing': purchasing.quantize(quantizer),
                        'gross': gross.quantize(quantizer),
                        'net': net.quantize(quantizer)
                        }

        return ''

    @classmethod
    def remove_orphan_costs(cls, sender, document, **kwargs):
        countries = [ str(c.id) for c in document.countries ]
        groups = [ str(g.id) for g in document.countries_groups ]
        for cost in document.costs:
            # First, remove all costs that do not have a corresponding country
            # or a corresponding countries group anymore
            if cost not in countries and cost not in groups and cost != 'rest':
                document.costs.pop(cost)
            # Then, remove costs for weights that do not exist anymore
            else:
                for w in document.costs[cost]:
                    if int(w) not in document.weights:
                        document.costs[cost].pop(w)

signals.pre_save.connect(Carrier.remove_orphan_costs, sender=Carrier)
