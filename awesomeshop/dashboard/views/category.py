from flask import redirect, request, url_for

from ... import app
from ...helpers import admin_required, render_template
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
        return redirect(url_for('dashboard_categories'))
    return render_template('dashboard/category.html', form=form)


@app.route('/dashboard/category-<category_id>/remove')
@admin_required
def dashboard_remove_category(category_id):
    Category.objects(id=category_id).delete()
    return redirect(url_for('dashboard_categories'))
