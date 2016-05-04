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
from flask_restful import Resource, reqparse, inputs
from marshmallow import Schema, fields, post_load

from ... import admin_required, app, rest
from ...marsh import Loc, MultiObjField, ObjField
from ...page.models import Page
from ...photo import Photo, PhotoSchema
from ..models.category import Category
from ..models.product import products, BaseProduct
from ..models.tax import Tax


class BaseProductSchemaForList(Schema):
    id = fields.String(dump_only=True)
    type = fields.String(dump_only=True)
    slug = fields.String(dump_only=True)
    path = fields.String(dump_only=True)
    reference = fields.String(dump_only=True)
    name = Loc(dump_only=True)
    main_photo = fields.Nested(PhotoSchema)
    net_price = fields.Function(serialize=lambda obj:
                                             str(obj.get_price_per_item().net))
    delay = fields.Function(serialize=lambda obj: obj.get_delay())
    overstock_delay = fields.Function(serialize=lambda obj:
                                                     obj.get_overstock_delay())
    # TODO Replace with some wrapper because stock belongs to regular products
    stock = fields.Integer(dump_only=True)


class RegularProductSchemaForList(BaseProductSchemaForList):
    pass

productschemaforlist = {
        'regular': RegularProductSchemaForList
        }


class BaseProductSchemaForAdminList(BaseProductSchemaForList):
    gross_price = fields.Function(serialize=lambda obj: str(
                                               obj.get_price_per_item().gross))
    on_sale = fields.Boolean(dump_only=True)


class RegularProductSchemaForAdminList(BaseProductSchemaForAdminList):
    stock_alert = fields.Integer()

productschemaforadminlist = {
        'regular': RegularProductSchemaForAdminList
        }


class BaseProductSchemaForEdition(Schema):
    id = fields.String(allow_none=True)
    type = fields.String(dump_only=True)
    slug = fields.String(required=True)
    reference = fields.String(required=True)
    name = fields.Dict(default={})
    description = fields.Dict(default={})
    documentation = ObjField(f='id', obj=Page)
    category = ObjField(f='id', obj=Category)
    keywords = fields.String(allow_none=True)
    photos = fields.Nested(PhotoSchema, many=True, dump_only=True)
    main_photo = fields.Nested(PhotoSchema, dump_only=True)
    on_sale = fields.Boolean(default=False)
    related_products = MultiObjField(f='id', obj=BaseProduct)
    stock = fields.Integer()

    def preinit_product(self, product, data):
        product.slug = data['slug']
        product.reference = data['reference']
        product.category = data.get('category', u'')
        product.documentation = data.get('documentation', u'')
        product.keywords = data.get('keywords', u'')
        product.on_sale = data.get('on_sale', False)
        product.name = data.get('name', {})
        product.description = data.get('description', {})
        product.related_products = data.get('related_products', [])
        return product


class RegularProductSchemaForEdition(BaseProductSchemaForEdition):
    tax = ObjField(f='id', obj=Tax)
    on_demand = fields.Boolean(allow_none=True, default=False)
    purchasing_price = fields.Decimal(as_string=True)
    gross_price = fields.Decimal(as_string=True, required=True)
    weight = fields.Integer()
    stock_alert = fields.Integer()

    @post_load
    def make_product(self, data):
        if 'id' in data:
            product = products['regular'].objects.get_or_404(id=data['id'])
        else:
            product = products['regular']()
        product = self.preinit_product(product, data)
        product.tax = data.get('tax', u'')
        product.on_demand = data.get('on_demand', False)
        product.purchasing_price = data.get('purchasing_price', '0.0')
        product.gross_price = data['gross_price']
        product.weight = data.get('weight', 0)
        product.stock = data.get('stock', 0)
        product.stock_alert = data.get('stock_alert', 0)
        product.save()
        return product

productschemaforedition = {
        'regular': RegularProductSchemaForEdition
        }


class BaseProductSchema(Schema):
    id = fields.String(dump_only=True)
    type = fields.String(dump_only=True)
    slug = fields.String(dump_only=True)
    path = fields.String(dump_only=True)
    reference = fields.String(dump_only=True)
    name = Loc(dump_only=True)
    description = fields.String(attribute='description_content',
                                dump_only=True)
    net_price = fields.Function(serialize=lambda obj:
                                             str(obj.get_price_per_item().net))
    photos = fields.Nested(PhotoSchema, many=True, dump_only=True)
    weight = fields.Function(serialize=lambda obj: obj.get_weight())
    related_products = fields.Nested(
                                BaseProductSchemaForList,
                                attribute='related_products_on_sale',
                                many=True,
                                dump_only=True
                                )
    documentation = fields.String(attribute='documentation_content',
                                  dump_only=True)
    delay = fields.Function(serialize=lambda obj: obj.get_delay())
    overstock_delay = fields.Function(serialize=lambda obj:
                                                     obj.get_overstock_delay())


class RegularProductSchema(BaseProductSchema):
    stock = fields.Integer(dump_only=True)


productschema = {
        'regular': RegularProductSchema
        }


products_adminreqparser = reqparse.RequestParser()
products_adminreqparser.add_argument('out_of_stock', type=inputs.boolean)
products_adminreqparser.add_argument('stock_lower_than_alert',
                                     type=inputs.boolean)


class ApiProducts(Resource):
    def get(self, product_type=None):
        """List all products

        The following (mutually exclusive) arguments are accepted:

        out_of_stock=true
            Only list products which are out of (real) stock

        stock_lower_than_alert=true
            Only list products for which the (real) stock is low

        If both are in use, out_of_stock has precedence
        """
        if product_type:
            product = products[product_type]
        else:
            product = BaseProduct
        if current_user.is_authenticated and current_user.is_admin:
            options = products_adminreqparser.parse_args()
            options = dict((k, v) for k, v in
                           options.iteritems() if v is not None)
            query = {}
            if product_type == 'regular' and 'out_of_stock' in options:
                if options.pop('out_of_stock'):
                    obj = product.objects(stock=0)
                else:
                    obj = product.objects(stock__gt=0)
            elif (product_type == 'regular' and
                  'stock_lower_than_alert' in options):
                if options.pop('stock_lower_than_alert'):
                    obj = product.objects.where(
                                'this.stock <= this.alert && this.stock != 0'
                                )
                else:
                    obj = product.objects.where('this.stock > this.alert')
            else:
                obj = product.objects
            if product_type:
                schema = productschemaforadminlist[product_type]
            else:
                schema = BaseProductSchemaForAdminList
            return schema(many=True).dump(obj).data
        else:
            if product_type:
                schema = productschemaforlist[product_type]
            else:
                schema = BaseProductSchemaForList
            return schema(many=True).dump(
                    product.objects(on_sale=True)
                    ).data

    @admin_required
    def post(self, product_type):
        schema = productschemaforedition[product_type]()
        data = request.get_json()
        data.pop('id', None)
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data


class ApiNewProducts(Resource):
    def get(self):
        today = datetime.datetime.now()
        age = datetime.timedelta(days=app.config['NEW_PRODUCTS_MAX_AGE'])
        date_limit = today - age
        return BaseProductSchemaForList(many=True).dump(
                BaseProduct.objects(created_at__gt=date_limit, on_sale=True)
                ).data


class ApiSubProductEdit(Resource):

    @admin_required
    def get(self, product_type, product_id):
        return productschemaforedition[product_type]().dump(
                products[product_type].objects.get_or_404(id=product_id)
                ).data

    @admin_required
    def put(self, product_type, product_id):
        schema = productschemaforedition[product_type]()
        data = request.get_json()
        data['id'] = product_id
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data

    @admin_required
    def delete(self, product_type, product_id):
        products[product_type].objects.get_or_404(id=product_id).delete()
        return {'status': 'OK'}


class ApiProductFromCatAndSlug(Resource):

    def get(self, category_id, product_slug):
        product = BaseProduct.objects.get_or_404(
                    category=category_id,
                    slug=product_slug
                    )
        schema = productschema[product.type]
        return schema().dump(product).data


class ApiProductFromId(Resource):

    def get(self, product_id):
        product = BaseProduct.objects.get_or_404(id=product_id)
        schema = productschema[product.type]
        return schema().dump(product).data


class ProductPhoto(Resource):

    @admin_required
    def post(self, product_id):
        product = BaseProduct.objects.get_or_404(id=product_id)
        photo = Photo.from_request(request.files['file'])
        product.photos.append(photo)
        product.save()
        return PhotoSchema().dump(photo).data


class DeleteProductPhoto(Resource):

    @admin_required
    def delete(self, product_id, filename):
        product = BaseProduct.objects.get_or_404(id=product_id)
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
        product = BaseProduct.objects.get_or_404(id=product_id)
        item = product.photos.pop(from_rank)
        product.photos.insert(to_rank, item)
        product.save()
        return {'status': 'OK'}

rest.add_resource(ApiProducts, '/api/product', '/api/product-<product_type>')
rest.add_resource(ApiNewProducts, '/api/newproducts')
rest.add_resource(ApiSubProductEdit,
                  '/api/product-<product_type>/<product_id>/edit')
rest.add_resource(ApiProductFromCatAndSlug,
                  '/api/product/catslug/<category_id>/<product_slug>')
rest.add_resource(ApiProductFromId, '/api/product/<product_id>')
rest.add_resource(ProductPhoto, '/api/product/<product_id>/photo')
rest.add_resource(DeleteProductPhoto,
                  '/api/product/<product_id>/photo/<filename>')
rest.add_resource(
        MoveProductPhoto,
        '/api/product/<product_id>/photo/<int:from_rank>/move/<int:to_rank>'
        )
