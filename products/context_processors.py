from .cart import Cart


def wishlist_context(request):
    wishlist_ids = request.session.get('wishlist', [])

    return {
        'wishlist_ids': wishlist_ids,
        'wishlist_count': len(wishlist_ids),
    }


def cart_context(request):
    cart = Cart(request)

    return {
        'cart_count': len(cart),
    }