from flask import redirect, request, url_for

from ... import app
from ...helpers import admin_required, render_template
from ...photo import Photo
from ...page.models import Page
from ..forms import PageForm


@app.route('/dashboard/pages-<pagetype>')
@admin_required
def dashboard_pages(pagetype):
    return render_template(
                'dashboard/pages.html',
                pagetype=pagetype,
                pages=Page.objects(pagetype=pagetype)
                )


@app.route('/dashboard/<pagetype>/page', methods=['GET', 'POST'])
@app.route('/dashboard/<pagetype>/page-<page_id>', methods=['GET', 'POST'])
@admin_required
def dashboard_page(pagetype, page_id=None):
    if page_id:
        page = Page.objects.get_or_404(pagetype=pagetype, id=page_id)
    else:
        page = Page(pagetype=pagetype)
    form = PageForm(request.form, page)
    if form.validate_on_submit():
        form.populate_obj(page)
        page.pagetype = pagetype
        page.save()
        return redirect(url_for('dashboard_pages', pagetype=pagetype))
    return render_template('dashboard/page.html', page=page, form=form, pagetype=pagetype)


@app.route('/dashboard/page/<pagetype>/<page_id>/remove')
@admin_required
def dashboard_remove_page(pagetype, page_id):
    Page.objects(pagetype=pagetype, id=page_id).delete()
    return redirect(url_for('dashboard_pages', pagetype=pagetype))


@app.route('/dashboard/page/<pagetype>/<page_id>/<direction>')
@admin_required
def dashboard_move_page(pagetype, page_id, direction):
    Page.objects.get_or_404(id=page_id).move(direction)
    return redirect(url_for('dashboard_pages', pagetype=pagetype))

@app.route('/dashboard/page/<pagetype>/<page_id>/addphoto', methods=['POST'])
@admin_required
def dashboard_add_page_photo(pagetype, page_id):
    page = Page.objects.get_or_404(id=page_id)
    for f in request.files.getlist('photo[]'):
        photo = Photo.from_request(f)
        page.photos.append(photo)
    page.save()
    return redirect(
                url_for('dashboard_page', pagetype=pagetype, \
                        page_id=page_id) + \
                '#pictures')


@app.route('/dashboard/page/<pagetype>/<page_id>/removephoto/<filename>')
@admin_required
def dashboard_remove_page_photo(pagetype, page_id, filename):
    page = Page.objects.get_or_404(id=page_id)
    for p in page.photos:
        if p.filename == filename:
            p.delete_files()
            page.photos.remove(p)
            break
    page.save()
    return redirect(url_for('dashboard_page', pagetype=pagetype, \
                            page_id=page_id) + \
                    '#pictures')
