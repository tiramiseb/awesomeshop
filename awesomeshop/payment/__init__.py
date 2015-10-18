from flask import redirect, url_for
from flask.ext.babel import _, lazy_gettext

from .mode import PaymentMode
from .payplug_awesomeshop import PayPlug

class SepaTransfer(PaymentMode):
    id = 'sepa_transfer'
    replay_button_text = lazy_gettext(
                            'See SEPA bank transfer information again'
                            )

    @property
    def text(self):
        return u'<i class="fa fa-exchange"></i> {}'.format(
                    _('SEPA bank transfer')
                    )

    def execute(self, order):
        return redirect(url_for('sepa_bank_transfer',
                                order_number=order.number))


modes = [
    PayPlug(),
    SepaTransfer()
    ]
