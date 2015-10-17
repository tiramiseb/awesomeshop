from .. import app
from ..helpers import render_front

@app.route('/')
def home():
    return render_front('home.html')
