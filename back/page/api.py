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
from flask_login import current_user
from flask_restful import Resource
from marshmallow import Schema, fields, post_load
from mongoengine import OperationError

from .. import admin_required, rest
from ..marsh import Loc
from ..photo import Photo, PhotoSchema
from ..shop.api.product import BaseProductSchemaForList
from .models import Page


class PageSchemaForList(Schema):
    id = fields.String()
    slug = fields.String()
    title = Loc()


class PageSchemaForAdminList(PageSchemaForList):
    in_menu = fields.Boolean()


class PageSchema(Schema):
    id = fields.String()
    pagetype = fields.String(required=True)
    slug = fields.String(required=True)
    in_menu = fields.Boolean(default=False)
    title = fields.Dict(default={})
    text = fields.Dict(default={})
    photos = fields.Nested(PhotoSchema, many=True, dump_only=True)

    @post_load
    def make_page(self, data):
        if 'id' in data:
            page = Page.objects.get_or_404(id=data['id'])
        else:
            page = Page()
        page.pagetype = data['pagetype']
        page.slug = data['slug']
        page.in_menu = data.get('in_menu', False)
        page.title = data.get('title', {})
        page.text = data.get('text', {})
        page.save()
        return page


class PageContentSchema(Schema):
    id = fields.String()
    pagetype = fields.String()
    slug = fields.String()
    title = Loc()
    content = fields.String()
    products = fields.Nested(
                    BaseProductSchemaForList,
                    attribute='on_sale_products',
                    many=True
                    )


class ApiPages(Resource):

    def get(self, page_type=None):
        if current_user.is_authenticated and current_user.is_admin:
            schema = PageSchemaForAdminList
        else:
            schema = PageSchemaForList
        if page_type:
            return schema(many=True).dump(
                                        Page.objects.filter(pagetype=page_type)
                                        ).data
        else:
            return schema(many=True).dump(Page.objects).data

    @admin_required
    def post(self):
        schema = PageSchema()
        data = request.get_json()
        data.pop('id', None)
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data


class ApiPage(Resource):

    @admin_required
    def get(self, page_id):
        return PageSchema().dump(Page.objects.get_or_404(id=page_id)).data

    @admin_required
    def put(self, page_id):
        schema = PageSchema()
        data = request.get_json()
        data['id'] = page_id
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data

    @admin_required
    def delete(self, page_id):
        try:
            Page.objects.get_or_404(id=page_id).delete()
        except OperationError as e:
            if re.match('Could not delete document '
                        '(.*Product.documentation refers to it)', e.message):
                abort(400, {
                    'type': 'message',
                    'message': ('Could not delete: '
                                'this documentation is used in a product.')
                    })
            raise
        return {'status': 'OK'}


class ApiPageContent(Resource):

    def get(self, page_type, page_slug):
        page = Page.objects.get_or_404(pagetype=page_type, slug=page_slug)
        return PageContentSchema().dump(page).data


class PagePhoto(Resource):

    @admin_required
    def post(self, page_id):
        page = Page.objects.get_or_404(id=page_id)
        photo = Photo.from_request(request.files['file'])
        page.photos.append(photo)
        page.save()
        return PhotoSchema().dump(photo).data


class DeletePagePhoto(Resource):

    @admin_required
    def delete(self, page_id, filename):
        page = Page.objects.get_or_404(id=page_id)
        for p in page.photos:
            if p.filename == filename:
                p.delete_files()
                page.photos.remove(p)
                break
        page.save()
        return {'status': 'OK'}


rest.add_resource(ApiPages, '/page', '/page-<page_type>')
rest.add_resource(ApiPage, '/page/<page_id>')
rest.add_resource(ApiPageContent, '/page-<page_type>/<page_slug>')
rest.add_resource(PagePhoto, '/page/<page_id>/photo')
rest.add_resource(DeletePagePhoto, '/page/<page_id>/photo/<filename>')
