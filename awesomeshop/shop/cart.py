from flask import session
from satchless import cart

from .models import Product

class CartLine(cart.CartLine):

    def get_stock(self):
        return self.product.get_stock() - self.quantity

    @property
    def weight(self):
        return self.product.weight * self.quantity

    def for_session(self):
        """Export data for session storage"""
        return {
            'product_id': str(self.product.id),
            'quantity': self.quantity
        }

    @classmethod
    def from_session(cls, session_data):
        """Create cart from session data"""
        product = Product.objects.get(id=session_data['product_id'])
        quantity = session_data['quantity']
        return cls(product, quantity)

class Cart(cart.Cart):

    def create_line(self, product, quantity, data):
        return CartLine(product, quantity, data)

    def quantity(self, product=None):
        """Return the quantity of products

        If "product" is None, returns total quantity of the cart
        If "product" is not none, returns total quantity for the product
        """
        if product:
            line = self.get_line(product)
            if line:
                return line.quantity
            return 0
        else:
            return sum(line.quantity for line in self)

    def weight(self, product=None):
        """Return the products weight

        If "product" is None, returns total weight of the cart
        If "product" is not none, returns total weight for the product
        """
        if product:
            line = self.get_line(product)
            if line:
                return line.weight
            return 0
        else:
            return sum(line.weight for line in self)

    # Session storage
    def to_session(self):
        """Export data for session storage"""
        session['cart'] = [ line.for_session() for line in self ]

    @classmethod
    def from_session(cls):
        """Create cart from session data"""
        cart = cls()
        if 'cart' in session:
            for line in session.get('cart'):
                try:
                    cart._state.append(CartLine.from_session(line))
                except Product.DoesNotExist:
                    pass
        return cart

    def add(self, product, quantity, replace=False):
        cart.Cart.add(self, product, quantity, replace=replace)
        self.to_session()
