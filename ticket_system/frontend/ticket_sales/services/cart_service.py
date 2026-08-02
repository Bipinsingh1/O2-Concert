"""Session-based cart for ticket purchases."""


CART_SESSION_KEY = 'ticket_cart'


def get_cart(request) -> dict:
    return request.session.get(CART_SESSION_KEY, {})


def add_to_cart(request, category_type: str, quantity: int = 1):
    cart = get_cart(request)
    cart[category_type] = cart.get(category_type, 0) + quantity
    request.session[CART_SESSION_KEY] = cart


def remove_from_cart(request, category_type: str):
    cart = get_cart(request)
    cart.pop(category_type, None)
    request.session[CART_SESSION_KEY] = cart


def clear_cart(request):
    request.session.pop(CART_SESSION_KEY, None)


def cart_total_items(request) -> int:
    return sum(get_cart(request).values())
