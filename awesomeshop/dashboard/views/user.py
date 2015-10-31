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

from flask import redirect, request, url_for

from ... import app
from ...rendering import admin_required, render_template
from ...auth.models import User, Address
from ..forms import UserForm, AddressForm

@app.route('/dashboard/users')
@admin_required
def dashboard_users():
    return render_template('dashboard/users.html', users=User.objects)

@app.route('/dashboard/user', methods=['GET', 'POST'])
@app.route('/dashboard/user-<user_id>', methods=['GET', 'POST'])
@admin_required
def dashboard_user(user_id=None):
    if user_id:
        user = User.objects.get_or_404(id=user_id)
        addresses = []
        for a in user.addresses:
            thisform = AddressForm(request.form, a, prefix=str(a.id))
            if thisform.validate_on_submit():
                thisform.populate_obj(a)
                a.save()
                return redirect(url_for('dashboard_user',
                                        user_id=user_id)+'#addresses')
            addresses.append(thisform)
        newaddress = AddressForm(request.form, prefix='new')
        if newaddress.validate_on_submit():
            a = Address()
            newaddress.populate_obj(a)
            a.user = user
            a.save()
            return redirect(url_for('dashboard_user',
                                    user_id=user_id)+'#addresses')
    else:
        user = User()
        addresses = None
        newaddress = None
    form = UserForm(request.form, user, prefix="user")
    if form.validate_on_submit():
        if form.email.data:
            user.email = form.email.data
        user.is_admin = form.is_admin.data
        if form.password.data:
            user.set_password(form.password.data)
        user.save()
        if user_id:
            return redirect(url_for('dashboard_users'))
        else:
            return redirect(url_for('dashboard_user', user_id=user.id))

    return render_template('dashboard/user.html', user_id=user_id,
                                                  form=form,
                                                  addresses=addresses,
                                                  newaddress=newaddress)

@app.route('/dashboard/user-<user_id>/remove')
@admin_required
def dashboard_remove_user(user_id):
    User.objects(id=user_id).delete()
    return redirect(url_for('dashboard_users'))

@app.route('/dashboard/user-<user_id>/remove-address-<address_id>')
@admin_required
def dashboard_remove_address(user_id, address_id):
    Address.objects(id=address_id).delete()
    return redirect(url_for('dashboard_user', user_id=user_id)+'#addresses')
