from ... import app
from ...helpers import admin_required, render_template
from ...shop.models import Order

# Load other views when running the app
from . import carrier
from . import category
from . import country
from . import order
from . import page
from . import product
from . import tax
from . import user

@app.route('/dashboard')
@app.route('/dashboard/')
@admin_required
def dashboard():
    paid_orders = Order.objects(status='payment_received').order_by('number')
    prep_orders = Order.objects(status='preparation').order_by('number')
    awaiting_payment_orders = Order.objects(status='awaiting_payment').order_by('number')
    return render_template('dashboard/home.html', paid_orders=paid_orders,
                           prep_orders=prep_orders,
                           awaiting_payment_orders=awaiting_payment_orders)
