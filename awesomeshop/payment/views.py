from flask.ext.login import current_user

from .. import app
from ..helpers import render_front, login_required
from ..shop.models import Order

@app.route('/orders/<order_number>/sepa_bank_transfer')
@login_required
def sepa_bank_transfer(order_number):
    order = Order.objects.get_or_404(number=order_number,
                                     customer=current_user.to_dbref())
    return render_front('payment/sepa_bank_transfer.html', order=order)

@app.route('/orders/<order_number>/payplug-ipn')
def payplug_ipn(order_number):
    pass

@app.route('/orders/<order_number>/payplug-return')
@login_required
def payplug_return(order_number):
    order = Order.objects.get_or_404(number=order_number,
                                     customer=current_user.to_dbref())
    if order.status == 'awaiting_payment' and order.payment_data:
        order.set_status('awaiting_provider')
        order.save()
        return render_front('payment/payplug_return.html', order=order)
    abort(400)

@app.route('/orders/<order_number>/payplug-cancel')
@login_required
def payplug_cancel(order_number):
    order = Order.objects.get_or_404(number=order_number,
                                     customer=current_user.to_dbref())
    order.payment_data = None
    order.save()
    return render_front('payment/payplug_cancel.html', order=order)
