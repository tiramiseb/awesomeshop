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

from marshmallow import fields

class Count(fields.Field):
    def _serialize(self, value, attr, obj):
        return value.count()

class LocName(fields.Field):
    def _serialize(self, value, attr, obj):
        return value.loc_name

class NetPrice(fields.Field):
    def _serialize(self, value, attr, obj):
        return str(value.quantize('0.01').net)

class ObjField(fields.Field):
    """
    Needed arguments:
    * f: the field for the object
    * obj: the object class
    """
    def _serialize(self, value, attr, obj):
        return getattr(value, self.metadata['f'])
    def _deserialize(self, value, attr, data):
        return self.metadata['obj'].objects.get(**{self.metadata['f']: value})
