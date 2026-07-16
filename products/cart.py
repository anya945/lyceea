from decimal import Decimal

from .models import Product


class Cart:
    SESSION_KEY = 'cart'

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(self.SESSION_KEY, {})

        if self.SESSION_KEY not in self.session:
            self.session[self.SESSION_KEY] = self.cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(
                    product.discount_price
                    if product.discount_price is not None
                    else product.price
                ),
            }

        quantity = int(quantity)

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        if self.cart[product_id]['quantity'] > product.stock:
            self.cart[product_id]['quantity'] = product.stock

        if self.cart[product_id]['quantity'] <= 0:
            self.remove(product)
            return

        self.save()

    def remove(self, product):
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session.pop(self.SESSION_KEY, None)
        self.cart = {}
        self.save()

    def __len__(self):
        return sum(
            item['quantity']
            for item in self.cart.values()
        )

    def __iter__(self):
        product_ids = self.cart.keys()

        products = (
            Product.objects
            .filter(
                id__in=product_ids,
                is_active=True,
            )
            .select_related('category')
            .prefetch_related('images')
        )

        cart = self.cart.copy()

        for product in products:
            product_id = str(product.id)
            cart[product_id]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = (
                item['price'] * item['quantity']
            )

            yield item

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )