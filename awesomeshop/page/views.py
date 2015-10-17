from flask import redirect, url_for

from .. import app
from ..helpers import render_front
from .models import Page

@app.route('/info')
@app.route('/info/')
def info_root():
    return redirect(url_for('doc', slug='about'))

@app.route('/info/<slug>')
def info(slug):
    page = Page.objects.get_or_404(slug=slug, pagetype='info')
    return render_front('page/page.html', page=page, active=page.id)

@app.route('/doc')
@app.route('/doc/')
def doc_root():
    return redirect(url_for('doc', slug='index'))

@app.route('/doc/<slug>')
def doc(slug):
    page = Page.objects.get_or_404(slug=slug, pagetype='doc')
    return render_front('page/page.html', page=page, active=page.id)
