# -*- coding: utf8 -*-

# Copyright 2016 Sébastien Maccagnoni
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

import cStringIO

from flask import request
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from . import app, _, _cur, _date

# How much to go down for...
subspace = 5   # a small space
space_10 = 12  # a "10 pt" line
space_12 = 15  # a "12 pt" line
space_14 = 17  # a "14 pt" line
space_20 = 24  # a "20 pt" line


def invoice(order):
    content = cStringIO.StringIO()
    c = canvas.Canvas(content, pagesize=A4)
    c.setTitle('{} - {}'.format(
        app.config['SHOP_NAME'],
        _('INVOICE_NUM_AND_DATE',
          NUM=order.invoice_full_number,
          DATE=_date(order.invoice_date)
          )
        ))
    c.setLineWidth(.3)

    x = 1*cm
    y = 28*cm
    # Title
    c.setFont('Helvetica', 20)
    c.drawString(x+0.5*cm, y, app.config['SHOP_NAME'])

    # URL
    y -= space_14
    c.setFont('Helvetica', 12)
    c.drawString(x+0.5*cm, y, request.url_root)

    # Order and invoice details
    y -= space_20
    c.setFont('Helvetica', 12)
    c.drawString(x, y, _('ORDER_NUM_AND_DATE',
                         NUM=order.full_number,
                         DATE=_date(order.date)))
    y -= space_12
    c.setFont('Helvetica-Bold', 12)
    c.drawString(x, y, _('INVOICE_NUM_AND_DATE',
                         NUM=order.invoice_full_number,
                         DATE=_date(order.invoice_date)))
    c.setFont('Helvetica', 12)
    y -= space_12

    if order.payment_date:
        c.drawString(x, y, _('PAYMENT_RECEIVED_ON_X',
                             DATE=_date(order.payment_date)))
        y -= space_12
        c.drawString(x, y, '{} {}'.format(
                                    _('PAYMENT_'),
                                    _('PAYMENT:'+order.payment_id)
                                    ))
        y -= space_12

    if order.shipping_date:
        c.drawString(x, y, _('SHIPPED_ON_X',
                             DATE=_date(order.shipping_date)))
        y -= space_12

    # Delivery address
    y -= space_12
    c.drawString(x, y, _('DELIVERY_ADDRESS'))
    y -= space_20
    for l in order.delivery.split('\n'):
        c.drawString(x, y, l)
        y -= space_12

    # Billing address
    c.setFont('Helvetica', 14)
    x = 10.5*cm
    y = (29.7-5.5)*cm-space_14
    for l in order.billing.split('\n'):
        c.drawString(x, y, l)
        y -= space_14

    # Products table
    c.setFont('Helvetica-Bold', 10)
    colref = 1.5*cm
    colprod = 7*cm
    coldetails = 7.5*cm
    colqty = 15*cm
    colunit = 17*cm
    coltotal = 19.5*cm
    tablestart = 18*cm
    y = tablestart
    c.line(1*cm, y, 20*cm, y)
    y -= space_10
    c.drawString(colref, y, _('REFERENCE'))
    c.drawString(colprod, y, _('PRODUCT'))
    c.drawRightString(colqty, y, _('QTY'))
    c.drawRightString(colunit, y, _('UNIT'))
    c.drawRightString(coltotal, y, _('TOTAL'))
    y -= subspace
    c.line(1*cm, y, 20*cm, y)
    # Products themselves
    c.setFont('Helvetica', 10)
    for l in order.products:
        y -= space_10
        c.drawString(colref, y, l.reference)
        c.drawString(colprod, y, l.name)
        c.drawRightString(colqty, y, unicode(l.quantity))
        c.drawRightString(colunit, y, _cur(l.net_price, order.currency))
        if l.product.type == 'kit':
            for detail in l.product.get_details(l.data):
                y -= space_10
                c.drawString(coldetails, y, '- {}× {}'.format(
                                    unicode(detail['quantity']),
                                    detail['name'].encode('utf-8')
                                    ))
        y -= subspace
        c.line(1*cm, y, 20*cm, y)
    # Subtotal
    y -= space_10
    c.drawString(colprod, y, _('SUBTOTAL'))
    c.drawRightString(coltotal, y, _cur(order.net_subtotal, order.currency))
    y -= subspace
    c.line(1*cm, y, 20*cm, y)
    # Shipping
    y -= space_10
    c.drawString(colprod, y, _('SHIPPING'))
    c.drawRightString(colunit, y, order.carrier_description)
    c.drawRightString(coltotal, y, _cur(order.net_shipping, order.currency))
    y -= subspace
    c.line(1*cm, y, 20*cm, y)
    # Total
    y -= space_12
    c.setFont('Helvetica-Bold', 12)
    c.drawString(colprod, y, _('TOTAL'))
    c.drawRightString(coltotal, y, _cur(order.net_total, order.currency))
    y -= subspace*1.2
    c.line(1*cm, y, 20*cm, y)
    c.line(1*cm, tablestart, 1*cm, y)
    c.line(20*cm, tablestart, 20*cm, y)
    y -= space_10
    c.setFont('Helvetica', 10)
    c.drawString(colref, y, _('LEGAL_NOTICE'))

    # Footer
    c.setFont('Helvetica', 10)
    y = 1*cm
    lines = app.config['ORDER_FOOTER'].split('\n')
    lines.reverse()
    for l in lines:
        c.drawCentredString(10.5*cm, y, l)
        y += space_10

    c.save()
    result = content.getvalue()
    content.close()
    return result
