# -*- coding: utf8 -*-

# Copyright 2016 Sébastien Maccagnoni-Munch
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

from flask import url_for
from flask_babel import _, format_date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from . import app

subspace = 5
space_10 = 12
space_12 = 15
space_14 = 17
space_20 = 24


def invoice(order):
    content = cStringIO.StringIO()
    c = canvas.Canvas(content, pagesize=A4)
    c.setLineWidth(.3)

    x = 1*cm
    y = 28*cm
    # Title
    c.setFont('Helvetica', 20)
    c.drawString(x+0.5*cm, y, app.config['SHOP_NAME'])

    # URL
    y -= space_14
    c.setFont('Helvetica', 12)
    c.drawString(x+0.5*cm, y, url_for('shop', _external=True))

    # Order and invoice details
    y -= space_20
    c.setFont('Helvetica', 12)
    c.drawString(x, y, _('Order %(number)s, on %(date)s',
                         number=order.full_number,
                         date=format_date(order.date)))
    y -= space_12
    c.setFont('Helvetica-Bold', 12)
    c.drawString(x, y, _('Invoice %(number)s, on %(date)s',
                         number=order.invoice_full_number,
                         date=format_date(order.invoice_date)))
    c.setFont('Helvetica', 12)
    y -= space_12

    if order.payment_date:
        c.drawString(x, y, _('Payment received on %(date)s',
                             date=format_date(order.payment_date)))
        y -= space_12
        c.drawString(x, y, _('Paid by %(description)s',
                             description=order.payment_description))
        y -= space_12

    if order.shipping_date:
        c.drawString(x, y, _('Shipped on %(date)s',
                             date=format_date(order.shipping_date)))
        y -= space_12

    # Delivery address
    y -= space_12
    c.drawString(x, y, _('Delivery address:'))
    y -= space_12
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
    colqty = 15*cm
    colunit = 17*cm
    coltotal = 19.5*cm
    tablestart = 18*cm
    y = tablestart
    c.line(1*cm, y, 20*cm, y)
    y -= space_10
    c.drawString(colref, y, _('Reference'))
    c.drawString(colprod, y, _('Product'))
    c.drawRightString(colqty, y, _('Qty'))
    c.drawRightString(colunit, y, _('Unit'))
    c.drawRightString(coltotal, y, _('Total'))
    y -= subspace
    c.line(1*cm, y, 20*cm, y)
    # Products themselves
    c.setFont('Helvetica', 10)
    for p in order.products:
        y -= space_10
        c.drawString(colref, y, p.reference)
        c.drawString(colprod, y, p.name)
        c.drawRightString(colqty, y, str(p.quantity))
        c.drawRightString(colunit, y, p.net_price)
        c.drawRightString(coltotal, y, p.line_net_price)
        y -= subspace
        c.line(1*cm, y, 20*cm, y)
    # Subtotal
    y -= space_10
    c.drawString(colprod, y, _('Subtotal'))
    c.drawRightString(coltotal, y, order.net_subtotal)
    y -= subspace
    c.line(1*cm, y, 20*cm, y)
    # Shipping
    y -= space_10
    c.drawString(colprod, y, _('Shipping: %(description)s',
                               description=order.carrier_description))
    c.drawRightString(coltotal, y, order.net_shipping)
    y -= subspace
    c.line(1*cm, y, 20*cm, y)
    # Total
    y -= space_12
    c.setFont('Helvetica-Bold', 12)
    c.drawString(colprod, y, _('Total'))
    c.drawRightString(coltotal, y, order.net_total)
    y -= subspace*1.2
    c.line(1*cm, y, 20*cm, y)
    c.line(1*cm, tablestart, 1*cm, y)
    c.line(20*cm, tablestart, 20*cm, y)
    y -= space_10
    c.setFont('Helvetica', 10)
    c.drawString(
            colref,
            y,
            _(u'TVA non applicable, article 293 B du Code général des impôts')
            )

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
