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

from mongoengine import signals
from flask import abort
from flask_babel import format_currency, lazy_gettext

from ... import app, db
from ...mail import send_mail
from ...auth.models import User
from ...payment.modes import get_mode
from ...shipping.models import Carrier
from .product import BaseProduct


class OrderProduct(db.EmbeddedDocument):
    reference = db.StringField(db_field='ref')
    gross_price = db.StringField(db_field='gprice')
    net_price = db.StringField(db_field='nprice')
    line_gross_price = db.StringField(db_field='lgprice')
    line_net_price = db.StringField(db_field='lnprice')
    quantity = db.IntField(db_field='qty')
    quantity_from_stock = db.IntField(db_field='stk')
    product = db.ReferenceField(BaseProduct)
    name = db.StringField()
    delay = db.IntField()
    data = db.DictField()

    def set_quantity(self, quantity):
        quantity, from_stock, delay = self.product.destock(quantity, self.data)
        self.quantity = quantity
        self.quantity_from_stock = from_stock
        self.delay = delay
        return delay

    def set_gross_price(self, price):
        self.gross_price = format_currency(price, app.config['CURRENCY'])

    def set_net_price(self, price):
        self.net_price = format_currency(price, app.config['CURRENCY'])

    def set_line_gross_price(self, price):
        self.line_gross_price = format_currency(price, app.config['CURRENCY'])

    def set_line_net_price(self, price):
        self.line_net_price = format_currency(price, app.config['CURRENCY'])

    def _put_back_in_stock(self):
        if self.quantity_from_stock:
            quantity = self.quantity_from_stock
        else:
            quantity = self.quantity
        self.product.restock(quantity, self.data)


order_states = {
    # 'name': (
    #   'color': 'highlight color',
    #   'next': ('next', 'states')
    #   )
    'unconfirmed': {
        'color': 'danger',
        'next': ('awaiting_payment', 'cancelled')
        },
    'awaiting_payment': {
        'color': 'warning',
        'next': ('awaiting_provider', 'payment_received', 'payment_failed',
                 'cancelled')
        },
    'awaiting_provider': {
        'color': 'info',
        'next': ('payment_received', 'payment_failed', 'cancelled')
        },
    'payment_received': {
        'color': 'success',
        'next': ('preparation', 'cancelled')
        },
    'payment_failed': {
        'color': 'danger',
        'next': ('awaiting_payment', 'payment_received', 'cancelled')
        },
    'preparation': {
        'color': 'info',
        'next': ('shipped', 'cancelled')
        },
    'shipped': {
        'color': 'success',
        'next': ('awaiting_return',)
        },
    'awaiting_return': {
        'color': 'warning',
        'next': ('refund',)
        },
    'refund': {
        'color': 'success',
        'next': ()
        },
    'cancelled': {
        'color': 'warning',
        'next': ()
        }
}


class InvalidNextStatus(Exception):
    pass


def next_invoice_number():
    last = Order.objects.only('invoice_number')\
                .order_by('-invoice_number').first()
    if last and last.invoice_number:
        return last.invoice_number + 1
    else:
        return 1


class Order(db.Document):
    customer = db.ReferenceField(User, db_field='cust')
    status = db.StringField(db_field='stat', default='unconfirmed')
    number = db.SequenceField(db_field='nb', unique=True, required=True)
    number_prefix = db.StringField(db_field='nb_pfix',
                                   default=app.config['ORDER_PREFIX'])
    date = db.DateTimeField(default=datetime.datetime.now)
    invoice_number = db.IntField(db_field='inb')
    invoice_number_prefix = db.StringField(
                                    db_field='inb_pfix',
                                    default=app.config['INVOICE_PREFIX']
                                    )
    invoice_date = db.DateTimeField(db_field='idate')
    delivery = db.StringField()
    billing = db.StringField(db_field='bill')
    billing_firstname = db.StringField(db_field='bill_fn')
    billing_lastname = db.StringField(db_field='bill_ln')
    products = db.EmbeddedDocumentListField(OrderProduct)
    gross_subtotal = db.StringField(db_field='gsub')
    net_subtotal = db.StringField(db_field='nsub')
    carrier = db.ReferenceField(Carrier)
    carrier_description = db.StringField(db_field='car_desc')
    gross_shipping = db.StringField(db_field='gship')
    net_shipping = db.StringField(db_field='nship')
    gross_total = db.StringField(db_field='gtot')
    net_total = db.StringField(db_field='ntot')
    numeric_total = db.DecimalField(db_field='tot')
    paper_invoice = db.BooleanField(db_field='paper')
    payment_id = db.StringField(db_field='p_id')
    payment_icon = db.StringField(db_field='p_ico')
    payment_description = db.StringField(db_field='p_desc')
    # Data for the payment, specific to the payment method (optional)
    payment_data = db.DynamicField(db_field='p_data')
    # Date when the payment is really confirmed
    payment_date = db.DateTimeField(db_field='p_date')
    # Message from the payment module
    payment_message = db.StringField(db_field='p_msg')
    accept_reused_package = db.BooleanField(db_field='reuse')
    shipping_date = db.DateTimeField(db_field='s_date')
    tracking_url = db.StringField(db_field='turl')
    tracking_number = db.StringField(db_field='tnum')
    delay = db.IntField()

    meta = {
        'ordering': ['-number']
    }

    @property
    def full_number(self):
        return u'{}{}'.format(self.number_prefix, self.number)

    @property
    def invoice_full_number(self):
        if self.invoice_number:
            return u'{}{}'.format(self.invoice_number_prefix,
                                  self.invoice_number)
        else:
            return u''

    @property
    def count_products(self):
        return sum([p.quantity for p in self.products])

    @property
    def status_color(self):
        return order_states[self.status]['color']

    def set_status(self, status):
        if status in order_states[self.status]['next']:
            self.status = status
            if status == 'awaiting_payment':
                self.invoice_number = next_invoice_number()
                self.invoice_number_prefix = app.config['INVOICE_PREFIX']
                self.invoice_date = datetime.datetime.now()
            elif status == 'payment_received':
                self.payment_date = datetime.datetime.now()
                send_mail(self.customer.email, 'payment_received',
                          order=self, locale=self.customer.locale)
                for adm in User.get_admins():
                    send_mail(adm.email, 'admin_payment_received', order=self)
            elif status == 'payment_failed':
                self.payment_date = datetime.datetime.now()
                send_mail(self.customer.email, 'payment_failed',
                          order=self, locale=self.customer.locale,
                          error=self.payment_message)
            elif status == 'shipped':
                self.shipping_date = datetime.datetime.now()
                send_mail(self.customer.email, 'shipped', order=self,
                          locale=self.customer.locale)
            elif status == 'cancelled':
                self._put_products_back_in_stock()
            self.save()
        else:
            raise InvalidNextStatus

    @property
    def next_states(self):
        return order_states[self.status]['next']

    @property
    def tracking(self):
        return not not self.carrier.tracking_url

    def set_delivery(self, address):
        self.delivery = address.human_readable

    def set_billing(self, address):
        self.billing = address.human_readable
        self.billing_firstname = address.firstname
        self.billing_lastname = address.lastname

    def set_subtotal(self, price):
        currency = app.config['CURRENCY']
        self.gross_subtotal = format_currency(price.gross, currency)
        self.net_subtotal = format_currency(price.net, currency)

    def set_shipping(self, price):
        currency = app.config['CURRENCY']
        self.gross_shipping = format_currency(price.gross, currency)
        self.net_shipping = format_currency(price.net, currency)

    def set_total(self, price):
        currency = app.config['CURRENCY']
        self.gross_total = format_currency(price.gross, currency)
        self.net_total = format_currency(price.net, currency)
        self.numeric_total = price.net

    def set_payment_mode(self, mode_id):
        self.payment_id = mode_id
        mode = get_mode(mode_id)
        self.payment_icon = mode.icon
        self.payment_description = unicode(mode.description)

    def trigger_payment(self):
        if self.status not in ('unconfirmed', 'awaiting_payment'):
            # A payment may be triggered only if the order
            # is not already paid or cancelled
            abort(403)
        mode = get_mode(self.payment_id)
        if not mode:
            abort(403)
        if self.status == 'unconfirmed':
            # Triggering the payment for the first time (thus confirming
            # the order) causes an invoice to be emitted
            self.set_status('awaiting_payment')
        payment_response = mode.trigger(self)
        self.save()
        payment_response['order'] = self
        return payment_response

    def set_tracking_number(self, number):
        url = self.carrier.tracking_url
        if url:
            self.tracking_url = url.replace('@', number)
            self.tracking_number = number

    def _put_products_back_in_stock(self):
        for prod in self.products:
            prod._put_back_in_stock()


def email_on_order_creation(sender, document, **kwargs):
    if kwargs['created']:
        for adm in User.get_admins():
            send_mail(adm.email, 'admin_new_order', order=document)

signals.post_save.connect(email_on_order_creation, sender=Order)
