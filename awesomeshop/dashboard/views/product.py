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
from ...helpers import admin_required, render_template
from ...photo import Photo
from ...page.models import Page
from ...shop.models import BaseProduct, product_types
from ..forms import get_product_form

@app.route('/dashboard/products')
@admin_required
def dashboard_products():
    return render_template('dashboard/products.html',
                           products=BaseProduct.objects)

@app.route('/dashboard/new-<product_type>-product', methods=['GET', 'POST'])
@app.route('/dashboard/product-<product_id>', methods=['GET', 'POST'])
@admin_required
def dashboard_product(product_id=None, product_type=None):
    if product_id:
        prod = BaseProduct.objects.get_or_404(id=product_id)
    else:
        prod = product_types[product_type]()
    form = get_product_form(request.form, prod)
    form.documentation.queryset = Page.objects(pagetype='doc')
    if form.validate_on_submit():
        form.populate_obj(prod)
        prod.save()
        if product_id:
            # For an existing product, go back to the products list
            return redirect(url_for('dashboard_products'))
        else:
            # For a new product, open the product page
            return redirect(url_for('dashboard_product', product_id=prod.id))
    return render_template('dashboard/product.html', product=prod,
                           form=form, photos=prod.photos)


@app.route('/dashboard/product-<product_id>/remove')
@admin_required
def dashboard_remove_product(product_id):
    BaseProduct.objects(id=product_id).delete()
    return redirect(url_for('dashboard_products'))


@app.route('/dashboard/product-<product_id>/addphoto', methods=['POST'])
@admin_required
def dashboard_add_product_photo(product_id):
    prod = BaseProduct.objects.get_or_404(id=product_id)
    for f in request.files.getlist('photo[]'):
        photo = Photo.from_request(f)
        prod.photos.append(photo)
    prod.save()
    return redirect(
                url_for('dashboard_product', product_id=product_id) + \
                '#pictures')


@app.route('/dashboard/product-<product_id>/removephoto/<filename>')
@admin_required
def dashboard_remove_product_photo(product_id, filename):
    prod = BaseProduct.objects.get_or_404(id=product_id)
    for p in prod.photos:
        if p.filename == filename:
            p.delete_files()
            prod.photos.remove(p)
            break
    prod.save()
    return redirect(url_for('dashboard_product', product_id=product_id) + \
                    '#pictures')
