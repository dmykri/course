from django.db import models

from Shop.models import Cart


def recalc_cart(cart):
    cart_data = cart.products.aggregate(models.Sum('final_price'), models.Sum('qty'))
    if cart_data.get('final_price__sum'):
        cart.final_price = cart_data['final_price__sum']
    else:
        cart.final_price = 0
        
    if cart_data.get('qty__sum'):
        cart.total_products = cart_data['qty__sum']
    else:
        cart.total_products = 0
    cart.save()

def amount_check():
    for cart in Cart.objects.filter(in_order=False):
        for cart_product in cart.products.all():
            product = cart_product.product
            if cart_product.qty > product.amount and product.amount != 0:
                cart_product.qty = product.amount
                cart_product.save()
            elif product.amount == 0:
                cart.products.remove(cart_product)
                cart_product.delete()
            recalc_cart(cart)
