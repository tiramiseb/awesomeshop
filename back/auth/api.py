# -*- coding: utf8 -*-

# Copyright 2015-2016 Sébastien Maccagnoni
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

from flask import abort, redirect, request, session
from flask_login import current_user, login_user, logout_user
from flask_restful import Resource
from marshmallow import Schema, fields, post_dump, post_load
from mongoengine import NotUniqueError

from .. import app, admin_required, login_required, rest
from ..marsh import Count, ObjField
from ..shipping.models import Country
from ..shop.api.dbcart import CartSchema
from .models import Address, User


class AddressSchema(Schema):
    id = fields.String()
    title = fields.String(required=True)
    firstname = fields.String(missing='')
    lastname = fields.String(required=True)
    address = fields.String(required=True)
    country = ObjField(f='code', obj=Country, required=True)
    phone = fields.String(default='')


class UserSchemaForList(Schema):
    id = fields.String()
    email = fields.Email()
    is_admin = fields.Boolean()
    addresses = Count()
    carts = Count()


class UserSchema(Schema):
    auth = fields.Constant(True, dump_only=True)
    waiting_for_confirmation = fields.Boolean(attribute='confirm_code',
                                              dump_only=True)
    id = fields.String(allow_none=True)
    email = fields.Email()
    is_admin = fields.Boolean(default=False)
    password = fields.String(load_only=True)
    addresses = fields.Nested(AddressSchema, many=True)
    carts = fields.Nested(CartSchema, many=True)
    latest_delivery_address = fields.String()
    latest_billing_address = fields.String()
    latest_delivery_as_billing = fields.Boolean()
    latest_carrier = fields.String()
    latest_payment = fields.String()
    latest_reused_package = fields.Boolean()
    locale = fields.String(allow_none=True)

    @post_dump
    def remove_unneeded_confirmation(self, data):
        if data['waiting_for_confirmation'] is None:
            data.pop('waiting_for_confirmation')
        return data

    @post_load
    def make_user(self, data):
        if 'id' in data:
            user = User.objects.get_or_404(id=data['id'])
        else:
            user = User()
        if 'email' in data:
            user.email = data['email']
            if not current_user.is_authenticated or not current_user.is_admin:
                user.send_confirmation_email()
        if current_user.is_authenticated and current_user.is_admin:
            # Only an admin can modify the admin state of a user
            if 'is_admin' in data:
                user.is_admin = data['is_admin']
        if 'password' in data:
            user.set_password(data['password'])
        if 'locale' in data:
            user.locale = data['locale']
        user.save()
        if 'addresses' in data:
            # Get a list of current addresses
            user_s_addresses = [unicode(i.id) for i in
                                Address.objects(user=user).only('id')]
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
                address.firstname = a.get('firstname', u'')
                address.lastname = a['lastname']
                address.address = a['address']
                address.country = a['country']
                address.phone = a.get('phone', u'')
                address.save()
            # Delete all addresses not in the request
            for a in user_s_addresses:
                Address.objects.get(id=a).delete()
        # Ignore carts
        return user


unauthentified_data = {
        'auth': False,
        'email': None,
        'is_admin': False
        }


class UserLogin(Resource):

    def post(self):
        data = request.get_json()
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            return unauthentified_data
        auth_ok = user.check_password(data['password'])
        if auth_ok:
            login_user(user)
            return UserSchema().dump(user).data
        else:
            return unauthentified_data


class UserData(Resource):

    def get(self):
        if current_user.is_authenticated:
            userdata = UserSchema().dump(current_user).data
            return userdata
        else:
            return unauthentified_data

    @login_required
    def put(self):
        schema = UserSchema()
        data = request.get_json()
        data['id'] = unicode(current_user.id)
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data

    @login_required
    def delete(self):
        current_user.delete()
        logout_user()
        return unauthentified_data


class UserLogout(Resource):

    @login_required
    def get(self):
        logout_user()
        return unauthentified_data


class SetLang(Resource):

    def put(self):
        language = request.get_json().get('lang')
        if language:
            if current_user.is_authenticated:
                # Save language in the user's preferences
                current_user.locale = language
                current_user.save()
                return {'status': 'ok'}
            else:
                # Store language in a cookie
                session['locale'] = language
                return {'status': 'ok'}


class Register(Resource):

    def post(self):
        schema = UserSchema()
        if current_user.is_authenticated:
            return schema.dump(current_user).data
        try:
            result, errors = schema.load(request.get_json())
        except NotUniqueError:
            abort(400, {'type': 'message', 'message': 'A user with this email address already exists'})
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        login_user(result)
        return schema.dump(result).data


class ResendConfirmationEmail(Resource):

    @login_required
    def get(self):
        current_user.send_confirmation_email()
        return {'status': 'ok'}


class ForceLogin(Resource):

    @login_required
    def get(self):
        return {'status': 'ok'}


class ApiUsers(Resource):

    @admin_required
    def get(self):
        return UserSchemaForList(many=True).dump(User.objects).data

    @admin_required
    def post(self):
        schema = UserSchema()
        data = request.get_json()
        data.pop('id', None)
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data


class ApiUser(Resource):

    @admin_required
    def get(self, user_id):
        return UserSchema().dump(User.objects.get_or_404(id=user_id)).data

    @admin_required
    def post(self, user_id):
        schema = UserSchema()
        data = request.get_json()
        data['id'] = user_id
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data

    @admin_required
    def delete(self, user_id):
        User.objects.get_or_404(id=user_id).delete()
        return {'status': 'OK'}

rest.add_resource(UserLogin, '/login')
rest.add_resource(UserData, '/userdata')
rest.add_resource(UserLogout, '/logout')
rest.add_resource(SetLang, '/setlang')
rest.add_resource(Register, '/register')
rest.add_resource(ResendConfirmationEmail, '/register/resend')
rest.add_resource(ForceLogin, '/forcelogin')
rest.add_resource(ApiUsers, '/user')
rest.add_resource(ApiUser, '/user/<user_id>')


@app.route(app.config['URL_PREFIX']+'/confirm/<code>')
@login_required
def confirm_email(code):
    if code == current_user.confirm_code:
        current_user.confirm_code = None
        current_user.save()
    # TODO Redirect the user to a specific message
    return redirect('/')
