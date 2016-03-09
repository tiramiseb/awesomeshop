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

from flask import abort, request
from flask_restful import Resource
from marshmallow import Schema, fields, post_load

from ... import admin_required, rest
from ...marsh import Loc, MultiObjField, ObjField
from ...page.models import Page
from ...photo import Photo, PhotoSchema
from ..models import Category, Product, Tax

class ProductSchemaForList(Schema):
    id = fields.String(dump_only=True)
    slug = fields.String(dump_only=True)
    reference = fields.String(dump_only=True)
    name = Loc(dump_only=True)
    on_sale = fields.Boolean(dump_only=True)
    stock = fields.Integer(dump_only=True)
    on_demand = fields.Boolean(dump_only=True)
    gross_price = fields.Decimal(dump_only=True, as_string=True)
    net_price = fields.Decimal(dump_only=True, as_string=True)
    main_photo = fields.Nested(PhotoSchema)

class ProductSchema(Schema):
    id = fields.String(allow_none=True)
    slug = fields.String(required=True)
    reference = fields.String(required=True)
    name = fields.Dict(default={})
    description = fields.Dict(default={})
    documentation = ObjField(f='id', obj=Page)
    category = ObjField(f='id', obj=Category)
    keywords = fields.String(allow_none=True)
    photos = fields.Nested(PhotoSchema, many=True, dump_only=True)
    tax = ObjField(f='id', obj=Tax)
    on_sale = fields.Boolean(default=False)
    related_products = MultiObjField(f='id', obj=Product)
    on_demand = fields.Boolean(allow_none=True, default=False)
    purchasing_price = fields.Decimal(as_string=True)
    gross_price = fields.Decimal(as_string=True, required=True)
    weight = fields.Integer()
    stock = fields.Integer()
    stock_alert = fields.Integer()

    @post_load
    def make_product(self, data):
        if 'id' in data:
            product = Product.objects.get_or_404(id=data['id'])
        else:
            product = Product()
        product.slug = data['slug']
        product.reference = data['reference']
        product.name = data.get('name', {})
        product.description = data.get('description', {})
        product.documentation = data.get('documentation', '')
        product.category = data.get('category', '')
        product.keywords = data.get('keywords', '')
        product.tax = data.get('tax', '')
        product.on_sale = data.get('on_sale', False)
        product.related_products = data.get('related_products', [])
        product.on_demand = data.get('on_demand', False)
        product.purchasing_price = data.get('purchasing_price', '0.0')
        product.gross_price = data['gross_price']
        product.weight = data.get('weight', 0)
        product.stock = data.get('stock', 0)
        product.stock_alert = data.get('stock_alert', 0)
        product.save()
        return product



class ApiProduct(Resource):
    
    @admin_required
    def get(self, product_id=None):
        if (product_id):
            return ProductSchema().dump(
                    Product.objects.get_or_404(id=product_id)
                    ).data
        else:
             return ProductSchemaForList(many=True).dump(
                     Product.objects()
                     ).data

    @admin_required
    def post(self, product_id=None):
        schema = ProductSchema()
        data = request.get_json()
        if product_id:
            data['id'] = product_id
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors })
        return schema.dump(result).data

    @admin_required
    def delete(self, product_id):
        Product.objects.get_or_404(id=product_id).delete()
        return { 'status': 'OK' }

class ProductPhoto(Resource):
    @admin_required
    def post(self, product_id):
        product = Product.objects.get_or_404(id=product_id)
        photo = Photo.from_request(request.files['file'])
        product.photos.append(photo)
        product.save()
        return PhotoSchema().dump(photo).data

class DeleteProductPhoto(Resource):
    @admin_required
    def delete(self, product_id, filename):
        product = Product.objects.get_or_404(id=product_id)
        for p in product.photos:
            if p.filename == filename:
                p.delete_files()
                product.photos.remove(p)
                break
        product.save()
        return { 'status': 'OK' }

class MoveProductPhoto(Resource):
    @admin_required
    def get(self, product_id, from_rank, to_rank):
        # TODO Test if from_rank and to_rank < len(product.photos)
        product = Product.objects.get_or_404(id=product_id)
        item = product.photos.pop(from_rank)
        product.photos.insert(to_rank, item)
        product.save()
        return { 'status': 'OK' }

rest.add_resource(ApiProduct, '/api/product', '/api/product/<product_id>')
rest.add_resource(ProductPhoto, '/api/product/<product_id>/photo')
rest.add_resource(DeleteProductPhoto, '/api/product/<product_id>/photo/<filename>')
rest.add_resource(MoveProductPhoto, '/api/product/<product_id>/photo/<int:from_rank>/move/<int:to_rank>')
