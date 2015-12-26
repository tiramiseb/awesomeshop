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

from .. import db, get_locale
from ..mongo import TranslationsField

class Country(db.Document):
    code = db.StringField()
    default_name = db.StringField(db_field='d_name')
    name = TranslationsField()

    meta = {
        'ordering': ['code']
    }

    @property
    def loc_name(self):
        return self.name.get(get_locale(), self.default_name)

    @property
    def prefixed_name(self):
        return u'{} - {}'.format(self.code, self.loc_name)

    def as_dict(self):
        return {
            'id': str(self.id),
            'code': self.code,
            'name': self.prefixed_name
            }



class CountriesGroup(db.Document):
    name = db.StringField()
    countries = db.ListField(db.ReferenceField(
                        Country,
                        reverse_delete_rule=db.DENY,
                        ))

    meta = {
        'ordering': ['name']
    }



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
    weights = db.SortedListField(db.IntField(choices=None))
    tracking_url = db.StringField(db_field='tr_url')
    costs = db.DictField()

