from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart(object):
    def __init__(self, request):
        """
        Initialize the cart.
        """
        # --------------------------------------------------------------------------------
        # NOTE: About django sessions
        # the django session makes the current session available in the request object
        # the session dictionary accepts any Python object by default that can be serialized to JSON
        #
        # set session like this:    request.session['foo'] = 'bar'
        # retrieve a session key:   request.session.get('foo')
        # delete a key:            del request.session['foo']
        #
        # All about session in django_3_by_examples.pdf PAGE 238
        # --------------------------------------------------------------------------------
        self.session = request.session
        # get the cart from the current session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # if no cart is present in the session; then
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        :product: The product instance to add or update in the cart
        :quantity: An optional integer with product quantity.
        :override_quantity: Boolean tha indicates whether the quantity needs to be overridden with the give qte
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # mark the session as 'modified' to make sure it gets saved
        self.session.modified = True    # tells Django that the session has been changed and needs to be saved.

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database
        """
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Remove cart from session
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
