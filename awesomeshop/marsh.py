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

from . import get_locale


class Count(fields.Field):
    """
    Dump only: count the number of objects in a queryset
    """
    def _serialize(self, value, attr, obj):
        if isinstance(value, list):
            return len(value)
        else:
            return value.count()


class Loc(fields.Field):
    """
    Dump only: localize a TranslationField
    """
    def _serialize(self, value, attr, obj):
        return value.get(get_locale(), '')


class LocObjField(fields.Field):
    """
    Dump only: localize a TranslationField from a linked object

    * f: the field in the object
    """
    def _serialize(self, value, attr, obj):
        return getattr(value, self.metadata['f']).get(get_locale(), '')


class NetPrice(fields.Field):
    """
    Dump only: net price for a Price object
    """
    def _serialize(self, value, attr, obj):
        return str(value.quantize('0.01').net)


class ObjField(fields.Field):
    """
    Dump: select a field from an object
    Load: select an object from the field value

    Needed arguments:
    * f: the field used to find the object
    * obj: the object class
    """
    def _serialize(self, value, attr, obj):
        if self.metadata['f'] == 'id':
            return str(getattr(value, self.metadata['f'], ''))
        else:
            return getattr(value, self.metadata['f'], '')

    def _deserialize(self, value, attr, data):
        if value:
            return self.metadata['obj'].objects.get(
                                                 **{self.metadata['f']: value})
        else:
            return None


class MultiObjField(fields.Field):
    """
    Dump: get a list of fields from a list of objects (mongoengine's ListField)
    Load: get a list of objects from a list of fields

    Needed arguments:
    * f: the field used to find the objects
    * obj: the object class
    """
    def _serialize(self, value, attr, obj):
        if self.metadata['f'] == 'id':
            return [str(v['id']) for v in value]
        else:
            return [getattr(v, self.metadata['f']) for v in value]

    def _deserialize(self, value, attr, data):
        return [self.metadata['obj'].objects.get(**{self.metadata['f']: v})
                for v in value]
