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
from flask_login import login_user, logout_user
from flask_restful import Resource
from marshmallow import Schema, fields, post_load

from .. import admin_required, login_required, rest
from ..marsh import Count, ObjField
from ..shipping.models import Country
from ..shop.api import CartSchema
from .models import Address, User

# Not using marshmallow_mongoengine here because it isn't made for modifying
# multiple documents as once. Here, addresses are presented like
# embeddedocuments to the users but they are in fact independent documents.

class AddressSchema(Schema):
    id = fields.String()
    title = fields.String(required=True)
    firstname = fields.String(missing='')
    lastname = fields.String(required=True)
    address = fields.String(required=True)
    country = ObjField(f='code', obj=Country, required=True)
    phone = fields.String(missing='')

class UserSimpleSchema(Schema):
    id = fields.String()
    email = fields.Email()
    addresses = Count()
    carts = Count()

class UserSchema(Schema):
    id = fields.String(allow_none=True)
    email = fields.Email(required=True)
    password = fields.String(load_only=True)
    addresses = fields.Nested(AddressSchema, many=True)
    carts = fields.Nested(CartSchema, many=True)

    @post_load
    def make_user(self, data):
        if 'id' in data:
            user = User.objects.get_or_404(id=data['id'])
        else:
            user = User()
        user.email = data['email']
        if 'password' in data:
            user.set_password(data['password'])
        user.save()
        # Get a list of current addresses
        user_s_addresses = [ str(i.id) for i in \
                                      Address.objects(user=user).only('id') ]
        # Save all addresses in the request
        for a in data['addresses']:
            address_id = a.get('id')
            if address_id and address_id in user_s_addresses:
                address = Address.objects.get(user=user, id=address_id)
                user_s_addresses.remove(address_id)
            else:
                address = Address()
            address.user = user
            address.title = a['title']
            address.firstname = a['firstname']
            address.lastname = a['lastname']
            address.address = a['address']
            address.country = a['country']
            address.phone = a['phone']
            address.save()
        # Delete all addresses not in the request
        for a in user_s_addresses:
            Address.objects.get(id=a).delete()
        # Ignore carts
        return user


class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            return { 'auth': False }
        auth_ok = user.check_password(data['password'])
        if auth_ok:
            login_user(user)
        return { 'auth': auth_ok }
rest.add_resource(UserLogin, '/api/login')

class UserLogout(Resource):
    @login_required
    def get(self):
        logout_user()
        return { 'auth': False }
rest.add_resource(UserLogout, '/api/logout')

class ApiUser(Resource):
    @admin_required
    def get(self, user_id=None):
        if (user_id):
            return UserSchema().dump(User.objects.get_or_404(id=user_id)).data
        else:
            return UserSimpleSchema(many=True).dump(User.objects).data

    @admin_required
    def post(self, user_id=None):
        schema = UserSchema()
        data = request.get_json()
        if user_id:
            data['id'] = user_id
        result, errors = schema.load(data)
        return schema.dump(result).data

    @admin_required
    def delete(self, user_id):
        User.objects.get_or_404(id=user_id).delete()
        return { 'status': 'OK' }
rest.add_resource(ApiUser, '/api/user', '/api/user/<user_id>')
