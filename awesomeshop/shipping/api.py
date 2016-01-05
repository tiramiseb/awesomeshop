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
from flask_babel import _
from flask_restful import Resource
from marshmallow import Schema, fields, post_load
from mongoengine import OperationError

from .. import admin_required, login_required, rest
from ..marsh import Count, MultiObjField
from .models import Country, CountriesGroup

class CountrySchemaForList(Schema):
    id = fields.String(dump_only=True)
    code = fields.String(dump_only=True)
    name = fields.String(attribute='prefixed_name', dump_only=True)

class CountrySchema(Schema):
    id = fields.String()
    code = fields.String(required=True)
    default_name = fields.String(required=True)
    name = fields.Dict(default={})

    @post_load
    def make_country(self, data):
        if 'id' in data:
            country = Country.objects.get_or_404(id=data['id'])
        else:
            country = Country()
        country.code = data['code']
        country.default_name = data['default_name']
        country.name = data.get('name', {})
        country.save()

class CountriesGroupSchemaForList(Schema):
    id = fields.String(dump_only=True)
    name = fields.String(dump_only=True)
    countries = Count()

class CountriesGroupSchema(Schema):
    id = fields.String()
    name = fields.String(required=True)
    countries = MultiObjField(f='code', obj=Country)

    @post_load
    def make_countriesgroup(self, data):
        if 'id' in data:
            group = CountriesGroup.objects.get_or_404(id=data['id'])
        else:
            group = CountriesGroup()
        group.name = data['name']
        group.countries = data['countries']
        group.save()

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

class ApiCountriesGroup(Resource):
    @admin_required
    def get(self, group_id=None):
        if group_id:
            return CountriesGroupSchema().dump(
                           CountriesGroup.objects.get_or_404(id=group_id)).data
        else:
            return CountriesGroupSchemaForList(many=True).dump(
                                                   CountriesGroup.objects).data
    @admin_required
    def post(self, group_id=None):
        schema = CountriesGroupSchema()
        data = request.get_json()
        if group_id:
            data['id'] = group_id
        result, errors = schema.load(data)
        return schema.dump(result).data

    @admin_required
    def delete(self, group_id):
        CountriesGroup.objects.get_or_404(id=group_id).delete()
        return { 'status': 'OK' }

rest.add_resource(ApiCountry, '/api/country', '/api/country/<country_id>')
rest.add_resource(ApiCountriesGroup, '/api/countriesgroup',
                                     '/api/countriesgroup/<group_id>')
