# -*- coding: utf8 -*-

# Copyright 2015-2016 Sébastien Maccagnoni-Munch
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

from flask import abort, request
from flask_login import current_user
from flask_restful import Resource
from marshmallow import Schema, fields, post_load

from ... import admin_required, app, rest
from ...marsh import Loc, MultiObjField, ObjField
from ...page.models import Page
from ...photo import Photo, PhotoSchema
from ..models import Category, Product, Tax


class ProductSchemaForList(Schema):
    id = fields.String(dump_only=True)
    slug = fields.String(dump_only=True)
    path = fields.String(dump_only=True)
    reference = fields.String(dump_only=True)
    name = Loc(dump_only=True)
    stock = fields.Integer(dump_only=True)
    on_demand = fields.Boolean(dump_only=True)
    net_price = fields.Decimal(dump_only=True, as_string=True)
    main_photo = fields.Nested(PhotoSchema)


class ProductSchemaForAdminList(ProductSchemaForList):
    gross_price = fields.Decimal(dump_only=True, as_string=True)
    on_sale = fields.Boolean(dump_only=True)


class ProductSchemaForEdition(Schema):
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


class ProductSchema(Schema):
    id = fields.String(dump_only=True)
    slug = fields.String(dump_only=True)
    path = fields.String(dump_only=True)
    reference = fields.String(dump_only=True)
    name = Loc(dump_only=True)
    description = fields.String(attribute='description_content',
                                dump_only=True)
    net_price = fields.Decimal(dump_only=True, as_string=True)
    photos = fields.Nested(PhotoSchema, many=True, dump_only=True)
    stock = fields.Integer(dump_only=True)
    weight = fields.Integer(dump_only=True)
    on_demand = fields.Boolean(dump_only=True)
    related_products = fields.Nested(
                                ProductSchemaForList,
                                attribute='related_products_on_sale',
                                many=True,
                                dump_only=True
                                )
    documentation = fields.String(attribute='documentation_content',
                                  dump_only=True)


class ApiProducts(Resource):
    def get(self):
        if current_user.is_authenticated and current_user.is_admin:
            return ProductSchemaForAdminList(many=True).dump(
                    Product.objects()
                    ).data
        else:
            return ProductSchemaForList(many=True).dump(
                    Product.objects(on_sale=True)
                    ).data

    @admin_required
    def post(self):
        schema = ProductSchemaForEdition()
        data = request.get_json()
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data


class ApiNewProducts(Resource):
    def get(self):
        today = datetime.datetime.now()
        age = datetime.timedelta(days=app.config['NEW_PRODUCTS_MAX_AGE'])
        date_limit = today - age
        return ProductSchemaForList(many=True).dump(
                Product.objects(created_at__gt=date_limit, on_sale=True)
                ).data


class ApiProductEdit(Resource):

    @admin_required
    def get(self, product_id):
        return ProductSchemaForEdition().dump(
                Product.objects.get_or_404(id=product_id)
                ).data

    @admin_required
    def post(self, product_id):
        schema = ProductSchemaForEdition()
        data = request.get_json()
        data['id'] = product_id
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data

    @admin_required
    def delete(self, product_id):
        Product.objects.get_or_404(id=product_id).delete()
        return {'status': 'OK'}


class ApiProductFromCatAndSlug(Resource):
    def get(self, category_id, product_slug):
        return ProductSchema().dump(
                Product.objects.get_or_404(
                    category=category_id,
                    slug=product_slug
                    )
                ).data


class ApiProductFromId(Resource):
    def get(self, product_id):
        return ProductSchema().dump(
                Product.objects.get_or_404(id=product_id)
                ).data


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
        return {'status': 'OK'}


class MoveProductPhoto(Resource):
    @admin_required
    def get(self, product_id, from_rank, to_rank):
        # TODO Test if from_rank and to_rank < len(product.photos)
        product = Product.objects.get_or_404(id=product_id)
        item = product.photos.pop(from_rank)
        product.photos.insert(to_rank, item)
        product.save()
        return {'status': 'OK'}

rest.add_resource(ApiProducts, '/api/product')
rest.add_resource(ApiNewProducts, '/api/newproduct')
rest.add_resource(ApiProductEdit, '/api/product/<product_id>/edit')
rest.add_resource(ApiProductFromId, '/api/product/<product_id>')
rest.add_resource(ApiProductFromCatAndSlug,
                  '/api/product/catslug/<category_id>/<product_slug>')
rest.add_resource(ProductPhoto, '/api/product/<product_id>/photo')
rest.add_resource(DeleteProductPhoto,
                  '/api/product/<product_id>/photo/<filename>')
rest.add_resource(
        MoveProductPhoto,
        '/api/product/<product_id>/photo/<int:from_rank>/move/<int:to_rank>'
        )
