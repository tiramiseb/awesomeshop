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

from flask import request
from flask_restful import Resource
from marshmallow import Schema, fields

from .. import login_required, rest
from .models import Country

class CountrySchema(Schema):
    id = fields.String()
    code = fields.String()
    name = fields.Function(lambda obj: obj.prefixed_name)


class Countries(Resource):
    @login_required
    def get(self):
        return CountrySchema(many=True).dump(Country.objects).data
rest.add_resource(Countries, '/api/countries')

