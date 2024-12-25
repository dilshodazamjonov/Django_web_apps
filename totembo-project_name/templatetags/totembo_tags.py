from django import template
from totembo.models import *

register = template.Library()


@register.simple_tag()
def get_categories():
    return Category.objects.filter(parent=None)

@register.simple_tag()
def get_products_tissot():
    products = Product.objects.filter(model__title='Tissot')
    return products

@register.simple_tag()
def get_products_casio():
    products = Product.objects.filter(model__title='Casio')
    return products

@register.simple_tag()
def get_recent_products():
    products = Product.objects.order_by('-id')[:4]
    return products

@register.simple_tag()
def get_normal_price(price):
    return f'{int(price):_}'.replace('_', ' ')

@register.simple_tag(takes_context=True)
def query_params(context, **kwargs):
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        if key == 'delete':
            for param in value.split(','):
                query.pop(param, None)
        else:
            query[key] = value

    return query.urlencode()

@register.simple_tag()
def get_favorites(user):
    favorites = FavoriteProduct.objects.filter(user=user)
    favorites = [i.product for i in favorites]
    return favorites

@register.simple_tag()
def sales_products():
    product_sales = Product.objects.all()
    product_sales= [i for i in product_sales if i.discount][:3]
    return product_sales

@register.simple_tag()
def get_discount_price(price, discount):
    percent = (price*discount) / 100
    price = price - percent
    return f'{int(price):_}'.replace('_', ' ')


@register.simple_tag()
def get_highest_rated_ones():
    products = Product.objects.all()
    highs_rated = products[::-1]
    high_rated = [product for product in highs_rated if product.average_rating > 0]
    return high_rated

