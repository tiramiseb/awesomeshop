# -*- coding: utf8 -*-

# Copyright 2015-2016 Sébastien Maccagnoni
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
from decimal import Decimal

from flask import abort, request
from flask_login import current_user
from flask_restful import Resource, reqparse, inputs
from marshmallow import Schema, fields, post_load, post_dump

from ... import admin_required, app, rest
from ...marsh import Loc, MultiObjField, ObjField
from ...page.models import Page
from ...photo import Photo, PhotoSchema
from ..models.category import Category
from ..models.product import products, BaseProduct, KitSubProduct, \
                             KitSubProductOption
from ..models.tax import Tax


class BaseProductSchemaForList(Schema):
    id = fields.String()
    type = fields.String()
    slug = fields.String()
    path = fields.String()
    reference = fields.String()
    name = Loc()
    main_photo = fields.Nested(PhotoSchema)
    lower_price = fields.Function(
                    lambda obj, ctx: str(obj.get_lower_price_per_item().net)
                    )
    net_price = fields.Function(
            lambda obj, ctx: str(obj.get_price_per_item(ctx.get('data')).net)
            )
    weight = fields.Function(lambda obj, ctx: obj.get_weight(ctx.get('data')))
    delay = fields.Function(lambda obj, ctx: obj.get_delay(ctx.get('data')))
    overstock_delay = fields.Function(
                    lambda obj, ctx: obj.get_overstock_delay(ctx.get('data'))
                    )
    stock = fields.Function(lambda obj, ctx: obj.get_stock(ctx.get('data')))
    details = fields.Function(lambda obj, c: obj.get_details(c.get('data')))
    static = fields.Boolean()


class RegularProductSchemaForList(BaseProductSchemaForList):
    pass


class KitProductSchemaForList(BaseProductSchemaForList):
    pass

productschemaforlist = {
        'regular': RegularProductSchemaForList,
        'kit': KitProductSchemaForList
        }


class BaseProductSchemaForAdminList(BaseProductSchemaForList):
    gross_price = fields.Function(
                                lambda obj: str(obj.get_price_per_item().gross)
                                )
    on_sale = fields.Boolean()
    internal_note = fields.String(attribute='internal_note_content')


class RegularProductSchemaForAdminList(BaseProductSchemaForAdminList):
    stock_alert = fields.Integer()


class KitProductSchemaForAdminList(BaseProductSchemaForAdminList):
    pass

productschemaforadminlist = {
        'regular': RegularProductSchemaForAdminList,
        'kit': KitProductSchemaForAdminList
        }


class BaseProductSchemaForEdition(Schema):
    id = fields.String(allow_none=True)
    type = fields.String(dump_only=True)
    slug = fields.String(required=True)
    path = fields.String(dump_only=True)
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
    internal_note = fields.String(allow_none=True)

    def preinit_product(self, product_type, data):
        if 'id' in data:
            product = products[product_type].objects.get_or_404(id=data['id'])
        else:
            product = products[product_type]()
        product.slug = data['slug']
        product.reference = data['reference']
        product.category = data.get('category', u'')
        product.documentation = data.get('documentation', u'')
        product.keywords = data.get('keywords', u'')
        product.on_sale = data.get('on_sale', False)
        product.name = data.get('name', {})
        product.description = data.get('description', {})
        product.related_products = data.get('related_products', [])
        product.internal_note = data.get('internal_note', u'')
        return product


class RegularProductSchemaForEdition(BaseProductSchemaForEdition):
    tax = ObjField(f='id', obj=Tax)
    on_demand = fields.Boolean(allow_none=True, default=False)
    purchasing_price = fields.Decimal()
    gross_price = fields.Decimal(required=True)
    weight = fields.Integer()
    stock = fields.Integer()
    stock_alert = fields.Integer()

    @post_load
    def make_product(self, data):
        product = self.preinit_product('regular', data)
        product.tax = data.get('tax', u'')
        product.on_demand = data.get('on_demand', False)
        product.purchasing_price = data.get('purchasing_price', '0.0')
        product.gross_price = data['gross_price']
        product.weight = data.get('weight', 0)
        product.stock = data.get('stock', 0)
        product.stock_alert = data.get('stock_alert', 0)
        product.save()
        return product


class BaseProductSchemaForKitSubProductOptionForEdition(Schema):
    id = fields.String(required=True)
    name = Loc(dump_only=True)
    main_photo = fields.Nested(PhotoSchema, dump_only=True)
    gross_price = fields.Function(
                                lambda obj: str(obj.get_price_per_item().gross)
                                )


class KitSubProductOptionSchemaForEdition(Schema):
    quantity = fields.Integer(required=True)
    product = fields.Nested(BaseProductSchemaForKitSubProductOptionForEdition)


class KitSubProductSchemaForEdition(Schema):
    title = fields.String(allow_none=True)
    options = fields.Nested(KitSubProductOptionSchemaForEdition, many=True)
    can_be_disabled = fields.Boolean(default=False)
    default = fields.String(allow_none=True)


class KitProductSchemaForEdition(BaseProductSchemaForEdition):
    products = fields.Nested(KitSubProductSchemaForEdition, many=True)
    tax = ObjField(f='id', obj=Tax)
    price_variation = fields.Decimal(required=True)
    amount_instead_of_percent = fields.Boolean(default=False)

    @post_load
    def make_product(self, data):
        product = self.preinit_product('kit', data)
        products = []
        for sub in data['products']:
            options = []
            for opt in sub['options']:
                options.append(KitSubProductOption(
                    quantity=opt['quantity'],
                    product=opt['product']['id']
                    ))
            products.append(KitSubProduct(
                title=sub.get('title'),
                options=options,
                can_be_disabled=sub.get('can_be_disabled'),
                default=sub.get('default')
                ))
        product.products = products
        product.tax = data.get('tax', u'')
        product.price_variation = data.get('price_variation', 0)
        product.amount_instead_of_percent = data.get(
                                                'amount_instead_of_percent',
                                                False
                                                )
        product.save()
        return product


productschemaforedition = {
        'regular': RegularProductSchemaForEdition,
        'kit': KitProductSchemaForEdition
        }


class BaseProductSchema(Schema):
    id = fields.String()
    type = fields.String()
    slug = fields.String()
    path = fields.String()
    reference = fields.String()
    name = Loc()
    description = fields.String(attribute='description_content')
    net_price = fields.Function(
                  lambda obj, ctx: str(obj.get_price_per_item(ctx['data']).net)
                  )
    photos = fields.Nested(PhotoSchema, many=True)
    weight = fields.Function(lambda obj, ctx: obj.get_weight(ctx['data']))
    related_products = fields.Nested(
                                BaseProductSchemaForList,
                                attribute='related_products_on_sale',
                                many=True
                                )
    documentation = fields.String(attribute='documentation_content')
    delay = fields.Function(lambda obj, ctx: obj.get_delay(ctx['data']))
    overstock_delay = fields.Function(
                          lambda obj, ctx: obj.get_overstock_delay(ctx['data'])
                          )
    stock = fields.Function(lambda obj, ctx: obj.get_stock(ctx['data']))


class RegularProductSchema(BaseProductSchema):
    pass


class BaseProductSchemaForKitSubProductOption(Schema):
    id = fields.String(required=True)
    reference = fields.String(required=True)
    name = Loc()
    net_price = fields.Function(
                    lambda obj: str(obj.get_price_per_item().net)
                    )
    main_photo = fields.Nested(PhotoSchema, dump_only=True)


class KitSubProductOptionSchema(Schema):
    quantity = fields.Integer()
    product = fields.Nested(BaseProductSchemaForKitSubProductOption)
    net_price = fields.Function(
                    lambda obj: str(obj.get_price().net)
                    )
    selected_string = fields.String()


class KitSubProductSchema(Schema):
    id = fields.String()
    title = fields.String()
    options = fields.Nested(KitSubProductOptionSchema, many=True)
    can_be_disabled = fields.Boolean()
    default = fields.String()
    selected = fields.Function(lambda o, c: o.get_selected_string(c['data']))
    reference_price = fields.Decimal()

    @post_dump
    def set_referenceprice(self, data):
        # Include as post_dump instead of using a Function so that the
        # "selected" value is known
        selected = data['selected']
        if selected == 'none':
            data['reference_price'] = '0.00'
        else:
            for o in data['options']:
                if '{}*{}'.format(
                                o['quantity'],
                                o['product']['id']
                                ) == selected:
                    data['reference_price'] = o['net_price']
                    break
        return data


class KitProductSchema(BaseProductSchema):
    products = fields.Nested(KitSubProductSchema, many=True)

productschema = {
        'regular': RegularProductSchema,
        'kit': KitProductSchema
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
                    obj = product.objects(stock=0, on_sale=True)
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


product_dataparser = reqparse.RequestParser()
product_dataparser.add_argument('data')


class ApiProductFromCatAndSlug(Resource):

    def get(self, category_id, product_slug):
        if current_user.is_authenticated and current_user.is_admin:
            product = BaseProduct.objects.get_or_404(
                        category=category_id,
                        slug=product_slug
                        )
        else:
            product = BaseProduct.objects.get_or_404(
                        category=category_id,
                        slug=product_slug,
                        on_sale=True
                        )
        schema = productschema[product.type]
        data = product_dataparser.parse_args()['data']
        if data:
            data = dict(i.split(':') for i in data.split(','))
        else:
            data = {}
        ctx = {'data': data}
        return schema(context=ctx).dump(product).data


class ApiProductFromId(Resource):

    def get(self, product_id):
        if current_user.is_authenticated and current_user.is_admin:
            product = BaseProduct.objects.get_or_404(id=product_id)
        else:
            product = BaseProduct.objects.get_or_404(id=product_id,
                                                     on_sale=True)
        schema = productschema[product.type]
        data = product_dataparser.parse_args()['data']
        if data:
            data = dict(i.split(':') for i in data.split(','))
        else:
            data = {}
        ctx = {'data': data}
        return schema(context=ctx).dump(product).data


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

rest.add_resource(ApiProducts, '/product', '/product-<product_type>')
rest.add_resource(ApiNewProducts, '/newproducts')
rest.add_resource(ApiSubProductEdit,
                  '/product-<product_type>/<product_id>/edit')
rest.add_resource(ApiProductFromCatAndSlug,
                  '/product/catslug/<category_id>/<product_slug>')
rest.add_resource(ApiProductFromId, '/product/<product_id>')
rest.add_resource(ProductPhoto, '/product/<product_id>/photo')
rest.add_resource(DeleteProductPhoto,
                  '/product/<product_id>/photo/<filename>')
rest.add_resource(
        MoveProductPhoto,
        '/product/<product_id>/photo/<int:from_rank>/move/<int:to_rank>'
        )
