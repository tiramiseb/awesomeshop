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

from flask import request
from flask_restful import Resource
from marshmallow import Schema, fields, pre_load

from ... import rest
from ...marsh import LocObjField, NetPrice
from ..models import Product
from .product import ProductSchema

class LiveCartlineSchema(Schema):
    product = fields.Dict()
    quantity = fields.Integer()

    @pre_load(pass_many=True)
    def use_existing_products(self, data, many):
        pschema = ProductSchema()
        newdata = []
        if not many:
            data = [data]
        for entry in data:
            try:
                prod = Product.objects.get(
                                id=entry['product']['id'],
                                on_sale=True
                                )
            except Product.DoesNotExist:
                # Forget non-existing products
                continue
            # Verify and adjust the quantity
            if prod.on_demand:
                quantity = entry['quantity']
            else:
                quantity = min(entry['quantity'], prod.stock)
            newdata.append({
                    'product': pschema.dump(prod).data,
                    'quantity': quantity
                    })
        if not many:
            if len(data) == 1:
                newdata = newdata[0]
            else:
                newdata = None
        return newdata

class CartlineSchema(LiveCartlineSchema):
    pass

class CartSchema(Schema):
    id = fields.String()
    name = fields.String(required=True)
    date = fields.DateTime()
    lines = fields.Nested(CartlineSchema, many=True)



class VerifyLiveCart(Resource):
    def post(self):
        schema = LiveCartlineSchema()
        data = request.get_json()
        result, errors = schema.load(data, many=True)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors })
        return result
rest.add_resource(VerifyLiveCart, '/api/cart/verify')
