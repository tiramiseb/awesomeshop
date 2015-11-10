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
from ...shop.models import Category
from ..forms import CategoryForm

@app.route('/dashboard/categories')
@admin_required
def dashboard_categories():
    return render_template('dashboard/categories.html',
                           categories=Category.hierarchy())

@app.route('/dashboard/category', methods=['GET', 'POST'])
@app.route('/dashboard/category-<category_id>', methods=['GET', 'POST'])
@admin_required
def dashboard_category(category_id=None):
    if category_id:
        cat = Category.objects.get_or_404(id=category_id)
    else:
        cat = Category()
    form = CategoryForm(request.form, cat)
    if form.validate_on_submit():
        form.populate_obj(cat)
        cat.save()
        return redirect(url_for('dashboard_category', category_id=cat.id))
    return render_template('dashboard/category.html', form=form, category=cat)


@app.route('/dashboard/category-<category_id>/remove')
@admin_required
def dashboard_remove_category(category_id):
    Category.objects(id=category_id).delete()
    return redirect(url_for('dashboard_categories'))
