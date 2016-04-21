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

from ... import admin_required, rest
from ..models.tax import Tax


class TaxSchema(Schema):
    id = fields.String()
    name = fields.String(required=True)
    rate = fields.Decimal(as_string=True, required=True)

    @post_load
    def make_tax(self, data):
        if 'id' in data:
            tax = Tax.objects.get_or_404(id=data['id'])
        else:
            tax = Tax()
        tax.name = data['name']
        tax.rate = data['rate']
        tax.save()
        return tax


class ApiTaxes(Resource):

    @admin_required
    def get(self):
        return TaxSchema(many=True).dump(Tax.objects).data

    @admin_required
    def post(self):
        schema = TaxSchema()
        data = request.get_json()
        data.pop('id', None)
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data


class ApiTax(Resource):

    @admin_required
    def get(self, tax_id):
        return TaxSchema().dump(Tax.objects.get_or_404(id=tax_id)).data

    @admin_required
    def put(self, tax_id):
        schema = TaxSchema()
        data = request.get_json()
        data['id'] = tax_id
        result, errors = schema.load(request.get_json())
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data

    @admin_required
    def delete(self, tax_id):
        Tax.objects.get_or_404(id=tax_id).delete()
        return {'status': 'OK'}

rest.add_resource(ApiTax, '/api/taxrate', '/api/taxrate/<tax_id>')
