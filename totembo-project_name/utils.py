from .models import Product, OrderProduct, Order, Customer
from django.contrib import messages

class CartForAuthenticatedUser:
    def __init__(self, request, products_slug=None, action=None):
        self.user = request.user
        self.request = request
        if products_slug and action:
            self.add_or_delete(products_slug, action)



    # Метод для получения товара из корзины
    def get_cart_info(self):
        customer, created = Customer.objects.get_or_create(user=self.user)

        order, created = Order.objects.get_or_create(customer=customer, payment=False)
        order_products = order.orderproduct_set.all()

        order_total_price = order.get_order_total_price
        order_total_quantity = order.get_order_total_quantity

        return {
            'order_total_price': order_total_price,
            'order_total_quantity': order_total_quantity,
            'order': order,
            'order_products': order_products
        }

    # Метод для добавления товара в корзину и его удаление
    def add_or_delete(self, product_slug, action):
        order = self.get_cart_info()['order']
        product = Product.objects.get(slug=product_slug)
        order_product, created = OrderProduct.objects.get_or_create(order=order, product=product)

        if action == 'add':
            if product.quantity > 0 and product.quantity > order_product.quantity:
                order_product.quantity += 1
                messages.success(self.request, f'Товар {product.title} добавлен в корзину')
            else:
                messages.error(self.request, f'Товар {product.title} выбран до максимум количеств!')
        elif action == 'delete':
            messages.success(self.request, f'Товар {product.title} успешно удален из корзины')
            order_product.quantity -= 1

        order_product.save()

        if order_product.quantity <= 0:
            order_product.delete()


    def clear_cart(self):
        order = self.get_cart_info()['order']
        order_products = order.orderproduct_set.all()
        for order_product in order_products:
            item = Product.objects.get(pk=order_product.product.pk)
            item.quantity -= order_product.quantity
            item.save()

        order.payment = True
        order.save()



# Функция для получения данных о корзина товаров
def get_cart_data(request):
    order = CartForAuthenticatedUser(request)
    order_info = order.get_cart_info()
    return order_info


