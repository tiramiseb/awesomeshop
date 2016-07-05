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

import re

from flask import abort, request
from flask_babel import _
from flask_login import current_user
from flask_restful import inputs, reqparse, Resource
from marshmallow import Schema, fields, post_load
from mongoengine import OperationError

from ... import admin_required, rest
from ...marsh import Count, Loc, ObjField
from ..models.category import Category
from .product import BaseProductSchemaForList


class CategorySchemaForList(Schema):
    id = fields.String()
    slug = fields.String()
    name = Loc()
    children = fields.Nested('CategorySchemaForList', many=True)
    products = Count(attribute='on_sale_products')


class CategorySchemaForFlatList(Schema):
    id = fields.String()
    path = fields.String()
    name = Loc()
    full_name = fields.String()
    products = Count(attribute='on_sale_products')
    level = fields.Integer()


class CategorySchemaForEdition(Schema):
    id = fields.String(allow_none=True)
    slug = fields.String(required=True)
    parent = ObjField(f='id', obj=Category)
    name = fields.Dict(default={})
    description = fields.Dict(default={})
    path = fields.String()

    @post_load
    def make_category(self, data):
        if 'id' in data:
            category = Category.objects.get_or_404(id=data['id'])
        else:
            category = Category()
        category.slug = data['slug']
        category.parent = data.get('parent', None)
        category.name = data.get('name', {})
        category.description = data.get('description', {})
        category.save()
        return category


class CategorySchema(Schema):
    id = fields.String()
    name = Loc()
    description = Loc()
    products = fields.Nested(
                    BaseProductSchemaForList,
                    attribute='recursive_on_sale_products',
                    many=True
                    )

reqparser = reqparse.RequestParser()
reqparser.add_argument('flat', type=inputs.boolean)


class ApiCategories(Resource):

    def get(self):
        options = reqparser.parse_args()
        if options.flat:
            return CategorySchemaForFlatList(many=True).dump(
                                            Category.ordered_all()
                                            ).data
        else:
            return CategorySchemaForList(many=True).dump(
                                            Category.objects(parent=None)
                                            ).data

    @admin_required
    def post(self):
        schema = CategorySchemaForEdition()
        data = request.get_json()
        data.pop('id', None)
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data


class ApiCategoryEdit(Resource):

    @admin_required
    def get(self, category_id):
        return CategorySchemaForEdition().dump(
                    Category.objects.get_or_404(id=category_id)
                    ).data

    @admin_required
    def put(self, category_id):
        schema = CategorySchemaForEdition()
        data = request.get_json()
        data['id'] = category_id
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data

    @admin_required
    def delete(self, category_id):
        try:
            Category.objects.get_or_404(id=category_id).delete()
        except OperationError as e:
            if re.match(
                 'Could not delete document (.*Product.category refers to it)',
                 e.message
                 ):
                abort(400, {
                  'type': 'message',
                  'message': _('Could not delete: this category has products.')
                  })
            elif e.message == \
                    'Could not delete document (Category.parent refers to it)':
                abort(400, {
                  'type': 'message',
                  'message': _('Could not delete: this category has children.')
                  })
            raise
        return {'status': 'OK'}


class ApiCategory(Resource):

    def get(self, category_id):
        return CategorySchema().dump(
                    Category.objects.get_or_404(id=category_id)
                    ).data

rest.add_resource(ApiCategories, '/api/category')
rest.add_resource(ApiCategoryEdit, '/api/category/<category_id>/edit')
rest.add_resource(ApiCategory, '/api/category/<category_id>')

# TODO: categories sorting
