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

from decimal import Decimal
import docutils.core
import re

from flask import abort, request
from flask_login import current_user
from flask_restful import Resource, reqparse, inputs
from marshmallow import Schema, fields, post_load
from prices import Price

from ... import app, get_locale, admin_required, login_required, rest
from ...marsh import Count, Loc, ObjField
from ...auth.models import Address
from ...shipping.models import Carrier
from ..models.order import Order, OrderProduct, InvalidNextStatus
from ..models.product import Product
from .product import ProductSchemaForList


class OrderProductCartSubSchema(Schema):
    id = fields.String(required=True)
    reference = fields.String(required=True)


class OrderProductCartSchema(Schema):
    product = fields.Nested(OrderProductCartSubSchema, required=True)
    quantity = fields.Integer(required=True)


class OrderProductSchema(Schema):
    reference = fields.String()
    gross_price = fields.String()
    net_price = fields.String()
    line_gross_price = fields.String()
    line_net_price = fields.String()
    quantity = fields.Integer()
    product = fields.Nested(ProductSchemaForList)
    name = fields.String()
    on_demand = fields.Boolean()
    data = fields.Raw()


class OrderSchemaForList(Schema):
    full_number = fields.String(dump_only=True)
    number = fields.String(dump_only=True)
    human_status = fields.String(dump_only=True)
    status_color = fields.String(dump_only=True)
    date = fields.Date(dump_only=True)
    products = fields.Integer(dump_only=True, attribute='count_products')
    net_total = fields.String(dump_only=True)


class OrderSchemaForAdminList(OrderSchemaForList):
    customer = fields.String(attribute='customer.email', dump_only=True)
    payment_date = fields.Date(dump_only=True)


class OrderSchema(Schema):
    """
    Can only be created, never modified except for the following fields:

    * status
    * tracking_number

    Modification of these fields must be done
    """
    # Fields that must be filled for creation
    delivery_address = fields.String(load_only=True, required=True)
    delivery_as_billing = fields.Boolean(load_only=True)
    billing_address = fields.String(load_only=True)
    cart = fields.Nested(OrderProductCartSchema, required=True,
                         load_only=True, many=True)
    carrier = fields.String(load_only=True, required=True)
    payment = fields.String(load_only=True)
    accept_reused_package = fields.Boolean()
    paper_invoice = fields.Boolean()

    # Fields that may be modified later (not by loading an order in the schema)
    status = fields.String(dump_only=True)
    tracking_number = fields.String(dump_only=True)

    # Fields that are only dumped
    human_status = fields.String(dump_only=True)
    status_color = fields.String(dump_only=True)
    full_number = fields.String(dump_only=True)
    number = fields.String(dump_only=True)
    date = fields.Date(dump_only=True)
    invoice_full_number = fields.String(dump_only=True)
    invoice_number = fields.String(dump_only=True)
    invoice_date = fields.Date(dump_only=True)
    delivery = fields.String(dump_only=True)
    billing = fields.String(dump_only=True)
    billing_firstname = fields.String(dump_only=True)
    billing_lastname = fields.String(dump_only=True)
    products = fields.Nested(OrderProductSchema, dump_only=True, many=True)
    gross_subtotal = fields.String(dump_only=True)
    net_subtotal = fields.String(dump_only=True)
    carrier_description = fields.String(dump_only=True)
    gross_shipping = fields.String(dump_only=True)
    net_shipping = fields.String(dump_only=True)
    gross_total = fields.String(dump_only=True)
    net_total = fields.String(dump_only=True)
    payment_icon = fields.String(dump_only=True)
    payment_description = fields.String(dump_only=True)
    payment_date = fields.Date(dump_only=True)
    payment_message = fields.String(dump_only=True)
    shipping_date = fields.Date(dump_only=True)
    tracking = fields.Boolean(dump_only=True)
    tracking_url = fields.String(dump_only=True)
    on_demand = fields.Boolean(dump_only=True)
    on_demand_delay_min = fields.Integer(dump_only=True)
    on_demand_delay_max = fields.Integer(dump_only=True)

    @post_load
    def make_order(self, data):
        """
        Execute it only when creating an order.

        An order must never be modified as a whole.
        """
        # TODO Error management would be needed here
        # (missing objects especially)
        order = Order()
        order.customer = current_user.to_dbref()
        delivery_address = Address.objects.get(id=data['delivery_address'])
        order.set_delivery(delivery_address)
        billing_address_id = data.get('billing_address', None)
        delivery_as_billing = data.get('delivery_as_billing', False)
        if not delivery_as_billing and billing_address_id:
            billing_address = Address.objects.get(id=billing_address_id)
        else:
            billing_address = delivery_address
        order.set_billing(billing_address)
        products = []
        subtotal = Price(0)
        total_weight = 0
        global_on_demand = False
        for productdata in data.get('cart', []):
            productobj = Product.objects.get(id=productdata['product']['id'])
            product = OrderProduct(
                reference=productdata['product']['reference'],
                product=productobj,
                name=productobj.name.get(get_locale(), u''),
                data=None
                )
            product.set_quantity(productdata['quantity'])
            global_on_demand = global_on_demand or product.on_demand
            quantity = product.quantity
            product.set_gross_price(productobj.gross_price)
            product.set_net_price(productobj.net_price)
            line_gross_price = productobj.gross_price * quantity
            line_net_price = productobj.net_price * quantity
            product.set_line_gross_price(line_gross_price)
            product.set_line_net_price(line_net_price)
            subtotal += Price(line_net_price, line_gross_price)
            total_weight += productobj.weight
            products.append(product)
        order.products = products
        order.set_subtotal(subtotal)
        carrierobj = Carrier.objects.get(id=data['carrier'])
        order.carrier = carrierobj
        order.carrier_description = carrierobj.full_description
        shipping_price = delivery_address.country.get_shipping_price(
                                                        carrierobj,
                                                        total_weight
                                                        )
        order.set_shipping(shipping_price)
        order.set_total(subtotal+shipping_price)
        order.set_payment_mode(data.get('payment'))
        order.accept_reused_package = data.get('accept_reused_package', False)
        order.paper_invoice = data.get('paper_invoice', False)
        order.on_demand = global_on_demand
        order.on_demand_delay_min = app.config['ON_DEMAND_DELAY_MIN']
        order.on_demand_delay_max = app.config['ON_DEMAND_DELAY_MAX']
        order.save()
        current_user.latest_delivery_address = str(delivery_address.id)
        current_user.latest_billing_address = str(billing_address.id)
        current_user.latest_delivery_as_billing = delivery_as_billing
        current_user.latest_carrier = str(carrierobj.id)
        current_user.latest_payment = order.payment_id
        current_user.latest_reused_package = order.accept_reused_package
        current_user.save()
        return order


class OrderSchemaForAdmin(OrderSchema):
    customer = fields.Nested('UserSchemaForList')
    next_states = fields.List(fields.String())


class PaymentInfoSchema(Schema):
    type = fields.String()
    message = fields.String()
    target = fields.String()
    order = fields.Nested(OrderSchema)


class ApiAllOrders(Resource):

    @admin_required
    def get(self):
        return OrderSchemaForAdminList(many=True).dump(Order.objects).data

orders_reqparser = reqparse.RequestParser()
orders_reqparser.add_argument('status')


class ApiOrders(Resource):

    def get(self):
        if current_user.is_admin:
            schema = OrderSchemaForAdminList
        else:
            schema = OrderSchemaForList
        options = orders_reqparser.parse_args()
        options = dict((k, v) for k, v in
                       options.iteritems() if v is not None)
        return schema(many=True).dump(
                    Order.objects(
                        customer=current_user.to_dbref(),
                        **options
                        )
                    ).data

    @login_required
    def post(self):
        schema = OrderSchema()
        data = request.get_json()
        result, errors = schema.load(data)
        if errors:
            abort(400, {'type': 'fields', 'errors': errors})
        return schema.dump(result).data


class ApiOrder(Resource):
    def get(self, number):
        if current_user.is_admin:
            return OrderSchemaForAdmin().dump(
                        Order.objects.get_or_404(
                            number=number
                            )
                        ).data
        else:
            return OrderSchema().dump(
                        Order.objects.get_or_404(
                            customer=current_user.to_dbref(),
                            number=number
                            )
                        ).data

    @admin_required
    def put(self, number):
        schema = OrderSchemaForAdmin()
        data = request.get_json()
        order = Order.objects.get_or_404(
                number=number
                )
        if 'status' in data:
            try:
                order.set_status(data['status'])
            except InvalidNextStatus:
                pass
        if 'tracking_number' in data and order.status == 'shipped':
                order.set_tracking_number(data['tracking_number'])
        order.save()
        return schema.dump(order).data


class PayOrder(Resource):
    def get(self, number):
        order = Order.objects.get_or_404(
                    customer=current_user.to_dbref(),
                    number=number
                    )
        payment_data = order.trigger_payment()
        if payment_data['type'] == 'message':
            payment_data['message'] = docutils.core.publish_parts(
                    source=payment_data['message'],
                    writer_name='html'
                    )['body']
        return PaymentInfoSchema().dump(payment_data).data

rest.add_resource(ApiAllOrders, '/api/order/all')
rest.add_resource(ApiOrders, '/api/order')
rest.add_resource(ApiOrder, '/api/order/<number>')
rest.add_resource(PayOrder, '/api/order/<number>/pay')
