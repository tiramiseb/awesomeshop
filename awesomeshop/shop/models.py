# -*- coding: utf8 -*-

import datetime

import docutils.core
import prices
from flask import abort
from flask.ext.babel import lazy_gettext
from mongoengine import signals
from satchless.item import StockedItem
from slugify import slugify

from .. import app, db, get_locale, payment
from ..mail import send_message
from ..mongo import TranslationsField
from ..photo import Photo
from ..auth.models import User
from ..page.models import Page
from ..shipping.models import Carrier
from . import UnknownStatus


class Tax(db.Document):
    name = db.StringField(required=True, max_length=100,
                          verbose_name=lazy_gettext('Name'))
    rate = db.DecimalField(verbose_name=lazy_gettext('Rate'), default=0)

    meta = {
        'ordering': ['name']
    }

    def __unicode__(self):
        return self.name


def next_category_rank():
    # Very very unlikely collisions, because new categories are created
    # only by an administrator
    last = Category.objects.only('rank').order_by('-rank').first()
    if last: return last.rank + 1
    else: return 1


class Category(db.Document):
    rank = db.IntField(required=True, unique=True, default=next_category_rank)
    slug = db.StringField(required=True, max_length=50,
                          verbose_name=lazy_gettext('Slug'))
    parent = db.ReferenceField('self', verbose_name=lazy_gettext('Parent'),
                               reverse_delete_rule=db.DENY)
    name = TranslationsField(max_length=50)

    meta = {
        'ordering': ['rank']
    }

    @property
    def short_name(self):
        return self.name.get(get_locale(), u'')

    @property
    def url(self):
        return Url.objects(document=self).only('url').first().url

    @property
    def nb_products(self):
        return Product.objects(category=self, on_sale=True).count()

    @property
    def onsale_products(self):
        return Product.objects(category=self, on_sale=True)

    @property
    def children(self):
        return Category.objects(parent=self)

    @property
    def onsale_products_recursive(self):
        p = list(self.onsale_products)
        for child in self.children:
            p.extend(child.onsale_products_recursive)
        p.sort(key=unicode)
        return p

    def __unicode__(self):
        if self.parent:
            return u'{} » {}'.format(self.parent.short_name,
                                          self.short_name)
        else:
            return unicode(self.short_name)

    @classmethod
    def hierarchy(cls, parent=None):
        hierarchy = []
        for o in cls.objects(parent=parent):
            hierarchy.append((o, cls.hierarchy(o.id)))
        return hierarchy



class Product(db.Document, StockedItem):
    on_sale = db.BooleanField(db_field='sale',
                              verbose_name=lazy_gettext('Is on sale'))
    slug = db.StringField(required=True, max_length=50,
                          verbose_name=lazy_gettext('Slug'))
    reference = db.StringField(db_field='ref',
                               max_length=50, unique=True, required=True,
                               verbose_name=lazy_gettext('Reference'))
    purchasing_price = db.DecimalField(
                            db_field='pprice',
                            verbose_name=lazy_gettext('Purchasing price')
                            )
    gross_price = db.DecimalField(
                            db_field='gprice',
                            required=True,
                            verbose_name=lazy_gettext('Gross price')
                            )
    tax = db.ReferenceField(Tax,
                            reverse_delete_rule=db.DENY,
                            verbose_name=lazy_gettext('Tax'))
    category = db.ReferenceField(Category, db_field='cat',
                                 reverse_delete_rule=db.DENY,
                                 verbose_name=lazy_gettext('Category'))
    weight = db.IntField(default=0, verbose_name=lazy_gettext('Weight'))# grams
    stock = db.IntField(default=0, verbose_name=lazy_gettext('Stock'))
    stock_alert = db.IntField(db_field='alert', default=0,
                              verbose_name=lazy_gettext('Stock alert'))
    documentation = db.ReferenceField(
                            Page,
                            db_field='doc',
                            reverse_delete_rule=db.DENY,
                            verbose_name=lazy_gettext('Documentation')
                            )
    name = TranslationsField(max_length=100, verbose_name=lazy_gettext('Name'))
    description = TranslationsField(db_field='desc',
                                    verbose_name=lazy_gettext('Description'))
    keywords = db.StringField(db_field='kw', max_length=200,
                              verbose_name=lazy_gettext('Keywords'))
    related_products = db.ListField(
                            db.ReferenceField('self'),
                            db_field='rel',
                            verbose_name=lazy_gettext('Related products')
                            )
    photos = db.EmbeddedDocumentListField(Photo)

    meta = {
        'ordering': ['reference']
    }

    def __unicode__(self):
        return self.name.get(get_locale(), u'')

    def __repr__(self):
        return unicode(self).encode('utf8')

    @property
    def output_description(self):
        parts = docutils.core.publish_parts(
                    source=self.description.get(get_locale(), u''),
                    writer_name='html')
        return parts['body']

    @property
    def output_documentation(self):
        parts = docutils.core.publish_parts(
                    source=self.documentation.text.get(get_locale(), u''),
                    settings_overrides = {
                        'initial_header_level': 3
                        },
                    writer_name='html')
        return parts['body']

    @property
    def url(self):
        return Url.objects(document=self).only('url').first().url

    def get_price_per_item(self):
        gross = self.gross_price
        net = gross * ( 1 + self.tax.rate )
        return prices.Price(net, gross)

    def get_stock(self):
        return self.stock

    @classmethod
    def remove_photos_from_disk(cls, sender, document, **kwargs):
        for p in document.photos:
            p.delete_files()

signals.pre_delete.connect(Product.remove_photos_from_disk, sender=Product)


def slugify_slug(sender, document, **kwargs):
    document.slug = slugify(document.slug)
signals.pre_save.connect(slugify_slug, sender=Category)
signals.pre_save.connect(slugify_slug, sender=Product)


class Url(db.Document):
    url = db.StringField(required=True, max_length=100)
    document = db.GenericReferenceField(db_field='doc')

def update_url(sender, document, url, created, **kwargs):
    if not created:
        remove_url(sender, document)
    Url(url=url, document=document).save()
def update_category_url(sender, document, **kwargs):
    if document.parent:
        url = document.parent.url + '/' + document.slug
    else:
        url = document.slug
    update_url(sender, document, url, **kwargs)
def update_product_url(sender, document, **kwargs):
    url = document.category.url + '/' + document.slug
    update_url(sender, document, url, **kwargs)
signals.post_save.connect(update_category_url, sender=Category)
signals.post_save.connect(update_product_url, sender=Product)

def remove_url(sender, document, **kwargs):
    Url.objects(document=document).delete()
signals.pre_delete.connect(remove_url, sender=Category)
signals.pre_delete.connect(remove_url, sender=Product)

class OrderProduct(db.EmbeddedDocument):
    reference = db.StringField(db_field='ref', max_length=50)
    gross_price = db.StringField(db_field='gprice')
    net_price = db.StringField(db_field='nprice')
    line_gross_price = db.StringField(db_field='lgprice')
    line_net_price = db.StringField(db_field='lnprice')
    quantity = db.IntField(db_field='qty')
    product = db.ReferenceField(Product)
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
    invoice_number_prefix = db.StringField(db_field='inb_pfix',
                                           default=app.config['INVOICE_PREFIX'])
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
            if type(prod.product) == Product:
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
