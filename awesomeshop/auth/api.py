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

from flask.ext.login import current_user
from flask_restful import Resource

from .. import rest
from .models import Address


class Preferences(Resource):
    def get(self):
        return current_user.preferences_as_dict()
rest.add_resource(Preferences, '/api/preferences')

class ApiAddresses(Resource):
    def get(self):
        return [ a.as_dict() for a in current_user.addresses ]
rest.add_resource(ApiAddresses, '/api/addresses')

class CarriersForAddress(Resource):
    def get(self, address_id, weight):
        address = Address.objects.get_or_404(user=current_user.to_dbref(), id=address_id)
        result = []
        for carrier in address.carriers(weight):
            result.append({
                'id': unicode(carrier[0].id),
                'name': carrier[0].description_and_name,
                'price': unicode(carrier[1]['net'])
                });
        return result
rest.add_resource(CarriersForAddress,
                  '/api/carriers-for-address/<string:address_id>/<int:weight>')
