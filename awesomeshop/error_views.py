from . import app
from .helpers import render_front

@app.errorhandler(500)
def page_not_found(e):
    return render_front('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_front('404.html'), 404

@app.errorhandler(403)
def page_not_found(e):
    return render_front('403.html'), 403

@app.errorhandler(400)
def page_not_found(e):
    return render_front('400.html'), 400

