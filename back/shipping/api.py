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
from marshmallow import Schema, fields, post_load, post_dump
from mongoengine import OperationError

from .. import admin_required, login_required, rest
from ..marsh import Count, Loc, MultiObjField
from .models import Country, CountriesGroup, Carrier, CarrierCosts, \
                    carriers_by_country_and_weight


class CountrySchemaForList(Schema):
    id = fields.String()
    code = fields.String()
    name = Loc(defaultfield='default_name')


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
        return country


class CountriesGroupSchemaForList(Schema):
    id = fields.String()
    name = fields.String()
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
        group.countries = data.get('countries', [])
        group.save()
        return group


class CarrierCostsSchema(Schema):
    weight = fields.Integer()
    costs = fields.Dict()

    @post_dump
    def costs_as_string(self, data):
        for cid, cost in data['costs'].iteritems():
            data['costs'][cid] = float(cost)


class CarrierSchemaForList(Schema):
    id = fields.String()
    name = fields.String()
    description = Loc()


class CarrierSchema(Schema):
    id = fields.String(allow_none=True)
    name = fields.String(required=True)
    description = fields.Dict(default={})
    tracking_url = fields.String()
    countries = MultiObjField(f='code', obj=Country)
    countries_groups = MultiObjField(f='id', obj=CountriesGroup)
    costs = fields.Nested(CarrierCostsSchema, many=True)

    @post_load
    def make_carrier(self, data):
        if 'id' in data:
            carrier = Carrier.objects.get_or_404(id=data['id'])
        else:
            carrier = Carrier()
        carrier.name = data['name']
        carrier.description = data.get('description', {})
        carrier.tracking_url = data.get('tracking_url', u'')
        carrier.countries = data.get('countries', [])
        carrier.countries_groups = data.get('countries_groups', [])
        carrier.costs = [CarrierCosts(weight=cost['weight'],
                                      costs=cost['costs'])
                         for cost in data['costs']]
        carrier.save()
        return carrier


class CarriersByCountryAndWeight(Schema):
    carrier = fields.Nested(CarrierSchemaForList)
    cost = fields.Decimal(as_string=True)


class ApiCountries(Resource):

    def get(self):
        return CountrySchemaForList(many=True).dump(Country.objects).data

    @admin_required
    def post(self):
        schema = CountrySchema()
        data = request.get_json()
        data.pop('id', None)
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data


class ApiCountry(Resource):

    @admin_required
    def get(self, country_id):
        return CountrySchema().dump(Country.objects.get_or_404(
                                                           id=country_id)).data

    @admin_required
    def put(self, country_id):
        schema = CountrySchema()
        data = request.get_json()
        data['id'] = country_id
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data

    @admin_required
    def delete(self, country_id):
        try:
            Country.objects.get_or_404(id=country_id).delete()
        except OperationError as e:
            if e.message == ('Could not delete document '
                             '(CountriesGroup.countries refers to it)'):
                abort(400, {
                    'type': 'message',
                    'message': _('Could not delete : this country '
                                 'is part of a countries group.')
                    })
            raise
        return {'status': 'OK'}


class ApiCountriesGroups(Resource):

    @admin_required
    def get(self):
        return CountriesGroupSchemaForList(many=True).dump(
                                                   CountriesGroup.objects).data

    @admin_required
    def post(self):
        schema = CountriesGroupSchema()
        data = request.get_json()
        data.pop('id', None)
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data


class ApiCountriesGroup(Resource):

    @admin_required
    def get(self, group_id):
        return CountriesGroupSchema().dump(
                           CountriesGroup.objects.get_or_404(id=group_id)).data

    @admin_required
    def put(self, group_id):
        schema = CountriesGroupSchema()
        data = request.get_json()
        data['id'] = group_id
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data

    @admin_required
    def delete(self, group_id):
        CountriesGroup.objects.get_or_404(id=group_id).delete()
        return {'status': 'OK'}


class ApiCarriers(Resource):

    @admin_required
    def get(self):
        return CarrierSchemaForList(many=True).dump(Carrier.objects).data

    @admin_required
    def post(self):
        schema = CarrierSchema()
        data = request.get_json()
        data.pop('id', None)
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data


class ApiCarrier(Resource):
    @admin_required
    def get(self, carrier_id):
        return CarrierSchema().dump(
                                Carrier.objects.get_or_404(id=carrier_id)).data

    @admin_required
    def put(self, carrier_id):
        schema = CarrierSchema()
        data = request.get_json()
        data['id'] = carrier_id
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data

    @admin_required
    def delete(self, carrier_id):
        Carrier.objects.get_or_404(id=carrier_id).delete()
        return {'status': 'OK'}


class ApiCarrierByWeight(Resource):
    def get(self, country, weight):
        result = carriers_by_country_and_weight(country, weight)
        return CarriersByCountryAndWeight(many=True).dump(result).data


rest.add_resource(ApiCountries, '/country')
rest.add_resource(ApiCountry, '/country/<country_id>')
rest.add_resource(ApiCountriesGroups, '/countriesgroup')
rest.add_resource(ApiCountriesGroup, '/countriesgroup/<group_id>')
rest.add_resource(ApiCarriers, '/carrier')
rest.add_resource(ApiCarrier, '/carrier/<carrier_id>')
rest.add_resource(ApiCarrierByWeight, '/carrier/<country>/<int:weight>')
