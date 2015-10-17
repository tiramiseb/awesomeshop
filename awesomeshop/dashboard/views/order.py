from flask import redirect, request, url_for

from ... import app
from ...helpers import admin_required, render_template
from ...shop.models import Order

@app.route('/dashboard/orders')
@admin_required
def dashboard_orders():
    return render_template('dashboard/orders.html',
                           orders=Order.objects)

@app.route('/dashboard/order-<order_number>')
@admin_required
def dashboard_order(order_number):
    order = Order.objects.get_or_404(number=order_number)
    return render_template('dashboard/order.html', order=order)


@app.route('/dashboard/order-<order_number>/status-<status>', methods=['GET', 'POST'])
@admin_required
def dashboard_change_order_status(order_number, status):
    order = Order.objects.get_or_404(number=order_number)
    if status == 'shipped' and order.carrier.tracking_url:
        order.set_tracking_number(request.form['tracking_number'])
    order.set_status(status)
    order.save()
    return redirect(url_for('dashboard_order', order_number=order_number))

#@app.route('/dashboard/order-<category_id>/remove')
#@admin_required
#def dashboard_remove_order(category_id):
#    Order.objects(id=order_id).delete()
#    return redirect(url_for('dashboard_orders'))
