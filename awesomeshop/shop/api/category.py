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

import re

from flask import abort, request
from flask_babel import _
from flask_login import current_user
from flask_restful import inputs, reqparse, Resource
from marshmallow import Schema, fields, post_load
from mongoengine import OperationError

from ... import admin_required, rest
from ...marsh import Loc, ObjField
from ..models import Category

class CategorySchemaForList(Schema):
    id = fields.String(dump_only=True)
    slug = fields.String(dump_only=True)
    name = Loc(dump_only=True)
    description = Loc(dump_only=True)
    children = fields.Nested('CategorySchemaForList', many=True)
    products = fields.Integer(dump_only=True)

class CategorySchemaForFlatList(Schema):
    id = fields.String(dump_only=True)
    slug = fields.String(dump_only=True)
    name = Loc(dump_only=True)
    full_name = fields.String(dump_only=True)
    description = Loc(dump_only=True)
    products = fields.Integer(dump_only=True)
    level = fields.Integer(dump_only=True)

class CategorySchema(Schema):
    id = fields.String(allow_none=True)
    slug = fields.String(required=True)
    parent = ObjField(f='id', obj=Category)
    name = fields.Dict(default={})
    description = fields.Dict(default={})

    @post_load
    def make_category(self, data):
        if 'id' in data:
            category = Category.objects.get_or_404(id=data['id'])
        else:
            category = Category()
        category.slug = data['slug']
        category.parent = data.get('parent', '')
        category.name = data.get('name', {})
        category.description = data.get('description', {})
        category.save()
        return category



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
        schema = CategorySchema()
        data = request.get_json()
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors })
        return schema.dump(result).data

class ApiCategory(Resource):
    
    @admin_required
    def get(self, category_id):
        return CategorySchema().dump(
                    Category.objects.get_or_404(id=category_id)
                    ).data

    @admin_required
    def post(self, category_id):
        schema = CategorySchema()
        data = request.get_json()
        data['id'] = category_id
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors })
        return schema.dump(result).data

    @admin_required
    def delete(self, category_id):
        try:
            Category.objects.get_or_404(id=category_id).delete()
        except OperationError as e:
            if re.match('Could not delete document (.*Product.category refers to it)', e.message):
                abort(400, { 'type': 'message', 'message': _('Could not delete : this category has products.')})
            elif e.message == 'Could not delete document (Category.parent refers to it)':
                abort(400, { 'type': 'message', 'message': _('Could not delete : this category has children.')})
            raise
        return { 'status': 'OK' }

rest.add_resource(ApiCategories, '/api/category')
rest.add_resource(ApiCategory, '/api/category/<category_id>')

# TODO: categories sorting
