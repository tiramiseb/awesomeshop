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

from flask import abort, current_app, redirect, request, url_for
from flask.ext.login import current_user
from satchless.item import InsufficientStock

from .. import app, payment, search as search_mod
from ..helpers import render_front, login_required
from ..auth.models import Address
from ..shipping.models import Carrier
from .models import Category, Product, Url, DbCart, Order, OrderProduct
from .cart import Cart

@app.route('/<path:path>')
def category_or_product(path):
    url = Url.objects.get_or_404(url=path.strip('/'))
    if type(url.document) == Category:
        return render_front('shop/category.html', category=url.document,
                            active=url.document.id)
    elif type (url.document) == Product and url.document.on_sale:
        return render_front('shop/product.html', product=url.document,
                            active=url.document.category.id)
    abort(404)
    
@app.route('/search')
def search():
    terms = request.args.get('q')
    return render_front('shop/search.html', terms=terms,
                        **search_mod.search(terms))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try: product_id = request.form['product']
    except: product_id = None
    if product_id:
        try: quantity = int(request.form['quantity'])
        except: quantity = 1
        try:
            Cart.from_session().add(Product.objects.get(id=product_id),
                                    quantity)
        except InsufficientStock:
            return render_front('shop/insufficient_stock.html',
                                next=request.args.get('next') or \
                                     request.referrer)
    return redirect(request.args.get('next') or \
                    request.referrer or \
                    url_for('home'))

@app.route('/cart/', methods=['GET', 'POST'])
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart = Cart.from_session()
    saved_cart = False
    if cart and request.method == 'POST':
        # Taken from login_required
        if 'save' in request.form:
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            saved_cart = DbCart.from_sessioncart(
                                cart,
                                request.form.get('cartname', '')
                                )
            saved_cart.save()
        else:
            for item in cart:
                inputname = 'quantity_{}'.format(item.product.id)
                if inputname in request.form:
                    try: quantity = int(request.form[inputname])
                    except: continue
                    try:
                        cart.add(item.product, quantity, replace=True)
                    except InsufficientStock:
                        return render_front('shop/insufficient_stock.html',
                                            next=request.args.get('next') or \
                                                 request.referrer)
    return render_front('shop/cart.html', cart=cart, saved_cart=saved_cart)

@app.route('/cart/remove-<product_id>')
def remove_from_cart(product_id):
    product = Product.objects.get_or_404(id=product_id)
    Cart.from_session().add(product, 0, replace=True)
    return redirect(url_for('cart'))

@app.route('/cart/empty')
def empty_cart():
    cart = Cart.from_session()
    cart.clear()
    cart.to_session()
    return redirect(url_for('home'))

@app.route('/cart/<cart_id>')
@login_required
def saved_cart(cart_id):
    cart = DbCart.objects.get_or_404(id=cart_id, user=current_user.to_dbref())
    return render_front('shop/saved_cart.html', saved_cart=cart)
    
@app.route('/cart/<cart_id>/delete')
@login_required
def delete_saved_cart(cart_id):
    DbCart.objects(id=cart_id, user=current_user.to_dbref()).delete()
    return redirect(url_for('carts'))
    
@app.route('/cart/<cart_id>/load')
@login_required
def load_saved_cart(cart_id):
    cart = DbCart.objects.get_or_404(id=cart_id, user=current_user.to_dbref())
    cart.to_session()
    cart.delete()
    return redirect(url_for('cart'))

@app.route('/checkout')
@login_required
def checkout():
    return render_front('shop/checkout.html', modes_of_payment=payment.modes)

@app.route('/confirm', methods=['POST'])
@login_required
def confirm_order():
    # If there is any error in gathering the data, tell it and don't go further
    try:
        # Get the cart
        cart = Cart.from_session()
        cart_total = cart.get_total().quantize('0.01')
        # Get data from the request
        delivery_id = request.form['delivery']
        billing_id = request.form['billing']
        carrier_id = request.form['shipping']
        payment_id = request.form['payment']
        accept_terms = request.form['accept_terms'] # Exception if terms
                                                    # are not accepted
        delivery_as_billing = not not request.form.get('delivery_as_billing')
        reused_package = not not request.form.get('reused_package')
        # Get data from the database
        delivery = Address.objects.get(id=delivery_id,
                                       user=current_user.to_dbref())
        if delivery_as_billing:
            billing = delivery
        else:
            billing = Address.objects.get(id=billing_id,
                                          user=current_user.to_dbref())
        carrier = Carrier.objects.get(id=carrier_id)
        carriers = delivery.carriers(cart.weight())
        for c in carriers:
            if c[0] == carrier:
                shipping_price = c[1]
                break
        shipping_price # Call it to raise an exception if it does not exist
    except:
        abort(400)
    #  TODO Move that to models.py
    # Create result
    order = Order()
    order.set_status('unconfirmed')
    order.customer = current_user.to_dbref()
    out_of_stock = []
    for line in cart:
        if line.product.stock < line.quantity:
            out_of_stock.append(line.product)
            Cart.from_session().add(line.product, line.product.stock, replace=True)
        else:
            order.products.append(OrderProduct.from_product(line.product,
                                                            line.quantity))
    if out_of_stock:
        return render_front('shop/out_of_stock_before_confirmation.html',
                            products=out_of_stock)
    order.set_delivery_address(delivery)
    order.set_billing_address(billing)
    order.set_subtotal(cart_total.gross, cart_total.net)
    order.set_carrier(carrier)
    order.set_shipping(shipping_price['gross'], shipping_price['net'])
    order.set_payment(payment_id)
    total_gross = cart_total.gross + shipping_price['gross']
    total_net = cart_total.net + shipping_price['net']
    order.set_total(total_gross, total_net)
    order.accept_reused_package = reused_package
    # A new loop because quantities should not be reduced if there is
    # at least one product without sufficient stock ("if out_of_stock" above)
    for line in cart:
        p = line.product
        p.stock -= line.quantity
        p.save()
    cart.clear()
    cart.to_session()
    order.save()
    # Save "preferences"
    current_user.latest_delivery_address = delivery_id
    current_user.latest_billing_address = carrier_id
    current_user.latest_delivery_as_billing = delivery_as_billing
    current_user.latest_carrier = carrier_id
    current_user.latest_payment = payment_id
    current_user.latest_reused_package = reused_package
    current_user.save()
    # ... and render the page :)
    return render_front('shop/confirm.html', order=order)

@app.route('/orders/<order_number>')
@login_required
def order(order_number):
    order = Order.objects.get_or_404(number=order_number)
    if order.customer == current_user.to_dbref() or current_user.is_admin:
        return render_front('shop/order.html', order=order)
    abort(404)

@app.route('/orders/<order_number>/confirm')
@login_required
def pay_order(order_number):
    order = Order.objects.get_or_404(number=order_number,
                                     customer=current_user.to_dbref())
    order.set_status('awaiting_payment')
    order.save()
    return order.execute_payment()

@app.route('/orders/<order_number>/cancel')
@login_required
def cancel_order(order_number):
    order = Order.objects.get_or_404(number=order_number,
                                     customer=current_user.to_dbref())
    order.set_status('cancelled')
    order.save()
    return redirect(url_for('order', order_number=order_number))
