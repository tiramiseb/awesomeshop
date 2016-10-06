# -*- coding: utf8 -*-

# Copyright 2015 Sébastien Maccagnoni
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

from flask import abort, request
from flask_login import current_user
from flask_restful import Resource
from marshmallow import Schema, fields, pre_load, post_load, post_dump

from ... import login_required, rest
from ...marsh import ObjField, NetPrice
from ..models.dbcart import DbCart, DbCartline
from ..models.product import BaseProduct
from .product import BaseProductSchemaForList


class LiveCartlineSchema(Schema):
    product = fields.Dict()
    data = fields.String(missing=None)
    quantity = fields.Integer()

    @pre_load(pass_many=True)
    def use_existing_products(self, data, many):
        newdata = []
        if not many:
            data = [data]
        for entry in data:
            try:
                prod = BaseProduct.objects.get(
                                id=entry['product']['id'],
                                on_sale=True
                                )
            except BaseProduct.DoesNotExist:
                # Forget non-existing products
                continue
            # Verify and adjust the quantity
            if prod.get_overstock_delay >= 0:
                quantity = entry['quantity']
            else:
                quantity = min(entry['quantity'], prod.get_stock())
            # Extract product data
            this_data_s = entry.get('data')
            if this_data_s:
                this_data = dict(i.split(':') for i in this_data_s.split(','))
            else:
                this_data = {}
            newdata.append({
                    'product': BaseProductSchemaForList(
                                            context={'data': this_data}
                                            ).dump(prod).data,
                    'data': this_data_s,
                    'quantity': quantity
                    })
        if not many:
            if len(data) == 1:
                newdata = newdata[0]
            else:
                newdata = None
        return newdata


class CartlineSchema(Schema):
    product = ObjField(f='id', obj=BaseProduct)
    data = fields.Dict(missing=None)
    quantity = fields.Integer()

    @pre_load(pass_many=True)
    def to_product_id(self, data, many):
        newdata = []
        if not many:
            data = [data]
        for entry in data:
            try:
                prod = BaseProduct.objects.get(
                                id=entry['product']['id'],
                                on_sale=True
                                )
            except BaseProduct.DoesNotExist:
                # Forget non-existing products
                continue
            this_data_s = entry['data']
            if isinstance(this_data_s, unicode) and this_data_s != u'':
                this_data = dict(i.split(':') for i in this_data_s.split(','))
            elif isinstance(this_data_s, dict):
                this_data = this_data_s
            else:
                this_data = {}
            newdata.append({
                    'product': prod.id,
                    'data': this_data,
                    'quantity': entry['quantity']
                    })
        if not many:
            if len(data) == 1:
                newdata = newdata[0]
            else:
                newdata = None
        return newdata

    @post_load
    def make_cartline(self, data):
        cartline = DbCartline()
        cartline.product = data['product']
        cartline.data = data['data']
        cartline.quantity = data['quantity']
        return cartline

    @post_dump(pass_many=True)
    def dump_cartline(self, data, many):
        newdata = []
        if not many:
            data = [data]
        for entry in data:
            try:
                prod = BaseProduct.objects.get(
                                id=entry['product'],
                                on_sale=True
                                )
            except BaseProduct.DoesNotExist:
                # Forget non-existing products
                continue
            # Extract product data
            this_data = entry.get('data')
            this_data_s = ','.join(':'.join(i) for i in this_data.items())
            newdata.append({
                    'product': BaseProductSchemaForList(
                                        context={'data': this_data}
                                        ).dump(prod).data,
                    'data': this_data_s,
                    'quantity': entry['quantity']
                    })
        if not many:
            if len(data) == 1:
                newdata = newdata[0]
            else:
                newdata = None
        return newdata


class CartSchema(Schema):
    id = fields.String()
    name = fields.String(required=True)
    date = fields.DateTime()
    lines = fields.Nested(CartlineSchema, many=True)

    @post_load
    def make_cart(self, data):
        cart = DbCart()
        cart.user = current_user.to_dbref()
        cart.name = data['name']
        lines, errors = CartlineSchema().load(data['lines'], many=True)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        cart.lines = lines
        cart.save()
        return cart


class VerifyLiveCart(Resource):
    def post(self):
        schema = LiveCartlineSchema()
        data = request.get_json()
        result, errors = schema.load(data, many=True)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return result


class ApiCarts(Resource):

    @login_required
    def get(self):
        return CartSchema(many=True).dump(DbCart.objects(
                                                user=current_user.to_dbref()
                                                )).data

    @login_required
    def post(self):
        schema = CartSchema()
        data = request.get_json()
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data


class ApiCart(Resource):

    @login_required
    def get(self, cart_id):
        return CartSchema().dump(DbCart.objects.get_or_404(
                                                user=current_user.to_dbref(),
                                                id=cart_id
                                                )).data

    @login_required
    def delete(self, cart_id):
        DbCart.objects.get_or_404(
                            user=current_user.to_dbref(),
                            id=cart_id
                            ).delete()
        return {'status': 'OK'}

rest.add_resource(VerifyLiveCart, '/cart/verify')
rest.add_resource(ApiCarts, '/cart')
rest.add_resource(ApiCart, '/cart/<cart_id>')
