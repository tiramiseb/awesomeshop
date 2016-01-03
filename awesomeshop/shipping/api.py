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
from flask.ext.babel import _
from flask_restful import Resource
from marshmallow import Schema, fields
from mongoengine import OperationError

from .. import admin_required, login_required, rest
from .models import Country

class CountrySchemaForList(Schema):
    id = fields.String()
    code = fields.String(dump_only=True)
    name = fields.String(attribute='prefixed_name', dump_only=True)

class CountrySchema(Schema):
    id = fields.String()
    code = fields.String(required=True)
    default_name = fields.String(required=True)
    name = fields.Dict(default={})

class ApiCountry(Resource):
    @login_required
    def get(self, country_id=None):
        if country_id:
            return CountrySchema().dump(Country.objects.get_or_404(
                                                           id=country_id)).data
        else:
            return CountrySchemaForList(many=True).dump(Country.objects).data

    @admin_required
    def post(self, country_id=None):
        schema = CountrySchema()
        data = request.get_json()
        if country_id:
            data['id'] = country_id
        result, errors = schema.load(data)
        return schema.dump(result).data

    @admin_required
    def delete(self, country_id):
        try:
            Country.objects.get_or_404(id=country_id).delete()
        except OperationError as e:
            if e.message == 'Could not delete document (CountriesGroup.countries refers to it)':
                abort(400, { 'type': 'message', 'message': _('Could not delete : this country is part of a countries group.')})
            raise
        return { 'status': 'OK' }

rest.add_resource(ApiCountry, '/api/country', '/api/country/<country_id>')

