from flask import redirect, request, url_for

from ... import app
from ...helpers import admin_required, render_template
from ...page.models import Page
from ...shop.models import Photo, Product
from ..forms import ProductForm

@app.route('/dashboard/products')
@admin_required
def dashboard_products():
    return render_template('dashboard/products.html',
                           products=Product.objects)

@app.route('/dashboard/product', methods=['GET', 'POST'])
@app.route('/dashboard/product-<product_id>', methods=['GET', 'POST'])
@admin_required
def dashboard_product(product_id=None):
    if product_id:
        prod = Product.objects.get_or_404(id=product_id)
    else:
        prod = Product()
    form = ProductForm(request.form, prod)
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
    Product.objects(id=product_id).delete()
    return redirect(url_for('dashboard_products'))


@app.route('/dashboard/product-<product_id>/addphoto', methods=['POST'])
@admin_required
def dashboard_add_product_photo(product_id):
    prod = Product.objects.get_or_404(id=product_id)
    for f in request.files.getlist('photo[]'):
        photo = Photo.from_request(f, 'products')
        prod.photos.append(photo)
    prod.save()
    return redirect(
                url_for('dashboard_product', product_id=product_id) + \
                '#pictures')


@app.route('/dashboard/product-<product_id>/removephoto/<filename>')
@admin_required
def dashboard_remove_product_photo(product_id, filename):
    prod = Product.objects.get_or_404(id=product_id)
    for p in prod.photos:
        if p.filename == filename:
            p.delete_files()
            prod.photos.remove(p)
            break
    prod.save()
    return redirect(url_for('dashboard_product', product_id=product_id) + \
                    '#pictures')
