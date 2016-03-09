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
from flask_restful import Resource
from marshmallow import Schema, fields, post_load
from mongoengine import OperationError

from .. import admin_required, rest
from ..marsh import Loc
from ..photo import Photo, PhotoSchema
from ..shop.api import ProductSchemaForList
from .models import Page


class PageSchemaForList(Schema):
    id = fields.String(dump_only=True)
    slug = fields.String(dump_only=True)
    title = Loc(dump_only=True)

class PageSchemaForAdminList(PageSchemaForList):
    in_menu = fields.Boolean(dump_only=True)


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
    pagetype = fields.String(dump_only=True)
    slug = fields.String(dump_only=True)
    title = Loc(dump_only=True)
    content = fields.String(dump_only=True)
    products = fields.Nested(ProductSchemaForList, many=True, dump_only=True)

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
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors })
        return schema.dump(result).data


class ApiPage(Resource):
    @admin_required
    def get(self, page_id=None):
        return PageSchema().dump(Page.objects.get_or_404(id=page_id)).data

    @admin_required
    def post(self, page_id):
        schema = PageSchema()
        data = request.get_json()
        data['id'] = page_id
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors })
        return schema.dump(result).data

    @admin_required
    def delete(self, page_id):
        try:
            Page.objects.get_or_404(id=page_id).delete()
        except OperationError as e:
            if re.match('Could not delete document (.*Product.documentation refers to it)', e.message):
                abort(400, { 'type': 'message', 'message': _('Could not delete : this documentation is used in a product.')})
            raise
        return { 'status': 'OK' }

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
        return { 'status': 'OK' }

class MovePage(Resource):
    @admin_required
    def get(self, page_id, target_id):
        page = Page.objects.get_or_404(id=page_id)
        if target_id == 'last':
            page.move_to_end()
        else:
            target = Page.objects.get(id=target_id)
            page.move_before(target)
        return { 'status': 'OK' }

rest.add_resource(ApiPages, '/api/page', '/api/page-<page_type>')
rest.add_resource(ApiPage, '/api/page/<page_id>')
rest.add_resource(ApiPageContent, '/api/page-<page_type>/<page_slug>')
rest.add_resource(PagePhoto, '/api/page/<page_id>/photo')
rest.add_resource(DeletePagePhoto, '/api/page/<page_id>/photo/<filename>')
rest.add_resource(MovePage, '/api/page/<page_id>/move/<target_id>')
