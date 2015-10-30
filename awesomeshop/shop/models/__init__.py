# -*- coding: utf8 -*-

# Copyright 2015 Sébastien Maccagnoni-Munch
#
# This file is part of AwesomeShop.
#
# AwesomeShop is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# AwesomeShop is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with AwesomeShop. If not, see <http://www.gnu.org/licenses/>.

import datetime

import prices
from flask import abort, session
from flask.ext.babel import _, lazy_gettext
from flask.ext.login import current_user
from mongoengine import signals
from slugify import slugify

from ... import app, db, get_locale, payment
from ...mail import send_message
from ...mongo import TranslationsField
from ...auth.models import User
from ...shipping.models import Carrier
from .. import UnknownStatus

from .category import *
from .product import *
from .tax import *
from .url import *



def slugify_slug(sender, document, **kwargs):
    document.slug = slugify(document.slug)
signals.pre_save.connect(slugify_slug, sender=Category)
signals.pre_save.connect(slugify_slug, sender=BaseProduct)



class DbCartLine(db.EmbeddedDocument):
    product = db.ReferenceField(BaseProduct, db_field='prod')
    quantity = db.IntField(db_field='qty')

    @property
    def available_quantity(self):
        return min(self.product.stock, self.quantity)

    def get_price_per_item(self):
        return self.product.get_price_per_item()

    def get_total(self):
        return self.get_price_per_item() * self.available_quantity

    def for_session(self):
        return {
            'product_id': str(self.product.id),
            'quantity': self.available_quantity
            }

class DbCart(db.Document):
    user = db.ReferenceField(User, required=True)
    date = db.DateTimeField(default=datetime.datetime.now)
    name = db.StringField()
    lines = db.EmbeddedDocumentListField(DbCartLine)

    meta = {
        'collection': 'cart',
        'ordering': ['-date']
    }

    @classmethod
    def from_sessioncart(cls, sessioncart, name=None):
        if not name:
            name = _('Unnamed cart')
        dbcart = cls(name=name, user=current_user.to_dbref())
        for line in sessioncart:
            dbcart.lines.append(
                            DbCartLine(
                                    product=line.product,
                                    quantity=line.quantity
                                    )
                            )
        return dbcart

    def to_session(self):
        lines = [ line.for_session() for line in self.lines ]
        session['cart'] = [ line for line in lines if line ]

    @property
    def formated_date(self):
        return self.date.strftime('%d/%m/%Y')

    @property
    def total_quantity(self):
        qty = 0
        for line in self.lines:
            qty += line.available_quantity
        return qty

    @property
    def total_price(self):
        price = prices.Price(0)
        for line in self.lines:
            price += line.product.get_price_per_item()*line.available_quantity
        return price

class OrderProduct(db.EmbeddedDocument):
    reference = db.StringField(db_field='ref', max_length=50)
    gross_price = db.StringField(db_field='gprice')
    net_price = db.StringField(db_field='nprice')
    line_gross_price = db.StringField(db_field='lgprice')
    line_net_price = db.StringField(db_field='lnprice')
    quantity = db.IntField(db_field='qty')
    product = db.ReferenceField(BaseProduct)
    name = db.StringField(max_length=100)

    @classmethod
    def from_product(cls, product, quantity):
        prices = product.get_price_per_item()
        gross_price = u'{} {}'.format(prices.quantize('0.01').gross,
                                      app.config['CURRENCY'])
        net_price = u'{} {}'.format(prices.quantize('0.01').net,
                                    app.config['CURRENCY'])
        line_prices = prices * quantity
        line_gross_price = u'{} {}'.format(line_prices.quantize('0.01').gross,
                                           app.config['CURRENCY'])
        line_net_price = u'{} {}'.format(line_prices.quantize('0.01').net,
                                         app.config['CURRENCY'])
        return cls(
                reference=product.reference,
                gross_price=gross_price,
                net_price=net_price,
                line_gross_price=line_gross_price,
                line_net_price=line_net_price,
                quantity=quantity,
                product=product,
                name=unicode(product)
                )

def next_invoice_number():
    last = Order.objects.only('invoice_number').order_by('-invoice_number').first()
    if not last or not last.invoice_number: return 1
    else: return last.invoice_number + 1
order_states = {
        # 'name': (
        #   lazy_gettext('verbose name'),
        #   'highlight color',
        #   ('next', 'states')
        #   )
        'unconfirmed': (
            lazy_gettext('unconfirmed'),
            'danger',
            ('awaiting_payment', 'cancelled')
            ),
        'awaiting_payment': (
            lazy_gettext('awaiting payment'),
            'warning',
            ('payment_received', 'payment_failed', 'cancelled')
            ),
        'awaiting_provider': (
            lazy_gettext('awaiting a response from the payment provider'),
            'info',
            ('payment_received', 'payment_failed', 'cancelled')
            ),
        'payment_received': (
            lazy_gettext('payment received'),
            'success',
            ('preparation', 'cancelled')
            ),
        'payment_failed': (
            lazy_gettext('payment failed ({})'),
            'danger',
            ('awaiting_payment', 'payment_received', 'cancelled')
            ),
        'preparation': (
            lazy_gettext('in preparation'),
            'info',
            ('shipped', 'cancelled')
            ),
        'shipped': (
            lazy_gettext('shipped on {}'),
            'success',
            ('awaiting_return',)
            ),
        'awaiting_return': (
            lazy_gettext('awaiting return'),
            'warning',
            ('refund',)
            ),
        'refund': (
            lazy_gettext('refund'),
            'success',
            ()
            ),
        'cancelled': (
            lazy_gettext('cancelled'),
            'warning',
            ()
            ),
}
class Order(db.Document):
    customer = db.ReferenceField(User, db_field='cust', required=True)
    # Use Order.set_status to set the status. Do not set it manually
    status = db.StringField(db_field='stat')
    number = db.SequenceField(db_field='nb', unique=True, required=True)
    number_prefix = db.StringField(db_field='nb_pfix',
                                   default=app.config['ORDER_PREFIX'])
    date = db.DateTimeField(default=datetime.datetime.now, required=True)
    invoice_number = db.IntField(db_field='inb', unique=True, sparse=True)
    invoice_number_prefix = db.StringField(
                                    db_field='inb_pfix',
                                    default=app.config['INVOICE_PREFIX']
                                    )
    invoice_date = db.DateTimeField(db_field='idate')
    delivery = db.StringField(required=True)
    billing = db.StringField(db_field='bill', required=True)
    billing_firstname = db.StringField(db_field='bill_fn', required=True)
    billing_lastname = db.StringField(db_field='bill_ln', required=True)
    products = db.EmbeddedDocumentListField(OrderProduct)
    gross_subtotal = db.StringField(db_field='gsub', required=True)
    net_subtotal = db.StringField(db_field='nsub', required=True)
    carrier = db.ReferenceField(Carrier)
    carrier_description = db.StringField(db_field='car_desc', required=True)
    gross_shipping = db.StringField(db_field='gship', required=True)
    net_shipping = db.StringField(db_field='nship', required=True)
    gross_total = db.StringField(db_field='gtot', required=True)
    net_total = db.StringField(db_field='ntot', required=True)
    numeric_total = db.DecimalField(db_field='tot', required=True)
    payment_id = db.StringField(db_field='p_id', required=True)
    payment_description = db.StringField(db_field='p_desc', required=True)
    payment_data = db.DynamicField(db_field='p_data')
    payment_date = db.DateTimeField(db_field='p_date')
    payment_message = db.StringField(db_field='p_msg')
    accept_reused_package = db.BooleanField(db_field='reuse', required=True)
    shipping_date = db.DateTimeField(db_field='s_date')
    tracking_url = db.StringField(db_field='turl')
    tracking_number = db.StringField(db_field='tnum')

    meta = {
        'ordering': ['-number']
    }

    @property
    def quantity(self):
        return sum([p.quantity for p in self.products])

    @property
    def full_number(self):
        return u'{}{}'.format(self.number_prefix, self.number)

    @property
    def formated_date(self):
        return self.date.strftime('%d/%m/%Y')

    @property
    def full_invoice_number(self):
        return u'{}{}'.format(self.invoice_number_prefix, self.invoice_number)

    @property
    def formated_invoice_date(self):
        return self.invoice_date.strftime('%d/%m/%Y')

    @property
    def formated_shipping_date(self):
        return self.shipping_date.strftime('%d/%m/%Y')

    @property
    def formated_payment_date(self):
        return self.payment_date.strftime('%d/%m/%Y')

    @property
    def human_status(self):
        text, color, next_ = order_states[self.status]
        if self.status == 'shipped':
            text = text.format(self.formated_shipping_date)
        elif self.status == 'payment_failed':
            text = text.format(self.payment_message)
        return u'<span class="text-{}">{}</span>'.format(color, text)

    def set_status(self, status):
        if status in order_states.keys():
            self.status = status
            if status == 'unconfirmed':
                self.payment_date = None
                self.payment_data = None
            elif status == 'awaiting_payment' and not self.invoice_number:
                self.invoice_number = next_invoice_number()
                self.invoice_number_prefix = app.config['INVOICE_PREFIX']
                self.invoice_date = datetime.datetime.now()
            elif status == 'payment_received':
                self.payment_date = datetime.datetime.now()
                send_message(self.customer.email, 'payment_received',
                             order=self, locale=self.customer.locale)
            elif status == 'payment_failed':
                self.payment_date = datetime.datetime.now()
                send_message(self.customer.email, 'payment_failed',
                             order=self, locale=self.customer.locale,
                             error=self.payment_message)
            elif status == 'shipped':
                self.shipping_date = datetime.datetime.now()
                send_message(self.customer.email, 'shipped', order=self)
            elif status == 'cancelled':
                self._put_products_back_in_stock()
        else:
            raise UnknownStatus

    def _put_products_back_in_stock(self):
        for prod in self.products:
            if prod.product._cls.starts_with('BaseProduct'):
                prod.product.stock += prod.quantity
                prod.product.save()

    @property
    def next_states(self):
        return order_states[self.status][2]

    def set_delivery_address(self, address):
        self.delivery = u'{} {}\n{}\n{}'.format(
                            address.firstname,
                            address.lastname,
                            address.address,
                            address.country)

    def set_billing_address(self, address):
        self.billing_firstname = address.firstname
        self.billing_lastname = address.lastname
        self.billing = u'{} {}\n{}\n{}'.format(
                            address.firstname,
                            address.lastname,
                            address.address,
                            address.country)

    def set_carrier(self, carrier):
        self.carrier = carrier
        self.carrier_description = unicode(carrier)

    def set_payment(self, pay):
        for mode in payment.modes:
            if mode.id == pay:
                self.payment_id = pay
                self.payment_description = mode.text
                return
        abort(400)

    def set_subtotal(self, gross, net):
        self.gross_subtotal = u'{} {}'.format(gross, app.config['CURRENCY'])
        self.net_subtotal = u'{} {}'.format(net, app.config['CURRENCY'])

    def set_shipping(self, gross, net):
        self.gross_shipping = u'{} {}'.format(gross, app.config['CURRENCY'])
        self.net_shipping = u'{} {}'.format(net, app.config['CURRENCY'])

    def set_total(self, gross, net):
        self.gross_total = u'{} {}'.format(gross, app.config['CURRENCY'])
        self.net_total = u'{} {}'.format(net, app.config['CURRENCY'])
        self.numeric_total = net

    def set_tracking_number(self, number):
        url = self.carrier.tracking_url
        if url:
            self.tracking_url = url.replace('@', number)
            self.tracking_number = number

    def execute_payment(self):
        if self.status not in ('unconfirmed', 'awaiting_payment'): abort(403)
        pay = None
        for m in payment.modes:
            if m.id == self.payment_id:
                pay = m
                break
        if not pay: abort(403)
        return pay.execute(self)

    @property
    def replay_payment_button_text(self):
        pay = None
        for m in payment.modes:
            if m.id == self.payment_id:
                pay = m
                break
        if not pay: abort(403)
        return pay.replay_button_text
