from flask.ext.login import current_user

from .. import app
from ..helpers import render_front, login_required
from ..shop.models import Order
from .payplug_awesomeshop import views

@app.route('/orders/<order_number>/sepa_bank_transfer')
@login_required
def sepa_bank_transfer(order_number):
    order = Order.objects.get_or_404(number=order_number,
                                     customer=current_user.to_dbref())
    return render_front('payment/sepa_bank_transfer.html', order=order)

