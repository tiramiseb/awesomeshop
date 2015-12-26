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

from marshmallow import Schema, fields

from ..marsh import LocObjField, NetPrice

class CartlineSchema(Schema):
    product = LocObjField(f='name')
    quantity = fields.Integer(dump_only=True)
    unit_price = NetPrice(dump_only=True)
    total_price = NetPrice(dump_only=True)


class CartSchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.String(dump_only=True)
    date = fields.DateTime(dump_only=True)
    lines = fields.Nested(CartlineSchema, dump_only=True, many=True)
    total_price = NetPrice(dump_only=True)
