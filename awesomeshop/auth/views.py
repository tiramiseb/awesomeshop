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

from flask import abort, redirect, request, session, url_for

from flask.ext.babel import _
from flask.ext.login import current_user, login_user, logout_user

from .. import app
from ..helpers import fresh_login_required, login_required, render_front, \
                      render_template
from ..shop.models import Order
from .models import User, Address
from .forms import LoginForm, RegisterForm, EmailPasswordForm, AddressForm

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get('next') or url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.objects.get(email=form.email.data)
        except User.DoesNotExist:
            user = None
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(request.args.get('next') or url_for('home'))
        form.email.errors.append(_('Email address or Password is invalid.'))
    return render_template('auth/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(request.args.get('next') or url_for('home'))

@app.route('/confirm/resend')
@login_required
def resend_confirmation_email():
    current_user.send_confirmation_email()
    return redirect(
                request.args.get('next') or request.referrer or url_for('home')
                )

@app.route('/confirm/<code>')
@login_required
def confirm_email(code):
    if code == current_user.confirm_code or not current_user.confirm_code:
        current_user.confirm_code = None
        current_user.save()
        return render_template('auth/email_verified.html')
    else:
        return render_template('auth/email_verification_failed.html')



@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(request.args.get('next') or url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            User.objects.get(email=form.email.data)
        except User.DoesNotExist:
            # Create the user if it is not already found
            user = User.register(form.email.data, form.password.data)
            user.save()
            login_user(user)
            return redirect(request.args.get('next') or '/')
        form.email.errors.append(_('You already have an account with this email address!'))
    return render_template('auth/register.html', form=form)

@app.route('/change_locale')
def change_locale():
    locale = request.args.get('locale')
    nexturl = request.args.get('next') or url_for('home')
    if locale:
        if current_user.is_authenticated:
            current_user.locale = locale
            current_user.save()
        else:
            session['locale'] = locale
    return redirect(nexturl)

@app.route('/profile/')
@app.route('/profile')
@login_required
def profile():
    return render_front('auth/profile.html')

@app.route('/profile/email_password', methods=['GET','POST'])
@fresh_login_required
def email_password():
    form = EmailPasswordForm()
    if request.method == 'GET':
        form.email.data = current_user.email
    else:
        if form.validate_on_submit():
            if form.email.data:
                current_user.set_email(form.email.data)
            if form.password.data:
                current_user.set_password(form.password.data)
            current_user.save()
    return render_front('auth/email_password.html', form=form)

@app.route('/profile/addresses', methods=['GET','POST'])
@login_required
def addresses():
    all_addresses_forms = []
    # Existing addresses
    for address in current_user.addresses:
        thisform = AddressForm(request.form, obj=address, prefix=str(address.id))
        if thisform.validate_on_submit():
            thisform.populate_obj(address)
            address.save()
            return redirect(url_for('addresses'))
        all_addresses_forms.append((address.id, thisform))
    # New address
    new_address_form = AddressForm(request.form, prefix='new')
    if new_address_form.validate_on_submit():
        new_address = Address(user=current_user.to_dbref())
        new_address_form.populate_obj(new_address)
        new_address.save()
        return redirect(url_for('addresses'))
    # Rendering
    return render_front(
                'auth/addresses.html',
                allforms=all_addresses_forms,
                newform=new_address_form
                )

@app.route('/profile/remove-address-<address_id>')
@login_required
def remove_address(address_id):
    address = Address.objects.get_or_404(user=current_user.to_dbref(), id=address_id)
    address.delete()
    return redirect(url_for('addresses'))

@app.route('/profile/delete', methods=['GET', 'POST'])
@login_required
def delete_profile():
    if request.method == 'POST':
        current_user.delete()
        logout_user()
        return redirect(url_for('home'))
    return render_front('auth/confirm_delete_account.html')

@app.route('/checkout/new_address-<address_destination>',
           methods=['GET','POST'])
@app.route('/checkout/address-<address_id>', methods=['GET','POST'])
@login_required
def address_from_checkout(address_id=None, address_destination=None):
    if address_id:
        address = Address.objects.get_or_404(user=current_user.to_dbref(), id=address_id)
    else:
        address = Address(user=current_user.to_dbref())
    form = AddressForm(request.form, address)
    if form.validate_on_submit():
        form.populate_obj(address)
        address.save()
        if address_destination == 'delivery':
            current_user.latest_delivery_address = str(address.id)
            current_user.save()
        elif address_destination == 'billing':
            current_user.latest_billing_address = str(address.id)
            current_user.save()
        return redirect(url_for('checkout'))
    return render_front('auth/address_from_checkout.html',
                        address_id=address_id, form=form)

@app.route('/orders')
@login_required
def orders():
    return render_front('auth/orders.html')
