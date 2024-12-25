from django.contrib.messages.context_processors import messages
from django.db import models
from django.db.models import Avg
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(unique=True, null=True, verbose_name='Слаг категории')
    icon = models.ImageField(upload_to='icons/', verbose_name='Иконка категории', null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                               null=True, blank=True, related_name='subcategories', verbose_name='Категория')
    image = models.ImageField(upload_to='category_image/', verbose_name='Фото категории', null=True, blank=True)
    def get_absolute_url(self):
        return reverse('category', kwargs={'slug':self.slug})

    def get_image(self):
        if self.image:
            return self.image
        else:
            return '⌚'

    def get_icon(self):
        if self.icon:
            return self.icon
        else:
            return '⌚'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'

class Brand(models.Model):
    title = models.CharField(max_length=150, verbose_name='Модель товара')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'

class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание товара')
    price = models.FloatField(verbose_name='Цена товара')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    color = models.CharField(max_length=100, verbose_name='Название цвета')
    color_code = models.CharField(max_length=100, verbose_name='Код цвета', default='#FFD700')
    size = models.CharField(max_length=10, verbose_name='Размер')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория товара')
    slug = models.SlugField(unique=True, null=True, verbose_name='Слаг категории')
    model = models.ForeignKey('Brand', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Модель')
    discount = models.IntegerField(blank=True, null=True, verbose_name='Скидка')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Дата добавление')
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='Дата Изменение')
    average_rating = models.FloatField(default=0, verbose_name='Средняя оценка')

    def calculate_average_rating(self):
        avg_rating = self.ratings.aggregate(Avg('star__value'))['star__value__avg']
        self.average_rating = avg_rating or 0
        self.save()

    def get_absolute_url(self):
        return reverse('product', kwargs={'slug': self.slug})

    def get_first_photo(self):
        if self.images:
            return self.images.first().image.url
        else:
            return '-'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

class ImageProduct(models.Model):
    image = models.ImageField(upload_to='images/', verbose_name='Фото товара')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')


    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Фото товара'
        verbose_name_plural = 'Фото товаров'


class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавление')

    def __str__(self):
        return f'Пользователь: {self.user.username}, Товар: {self.product.title}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные товары'

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    def __str__(self):
        return f'Покупатель: {self.user}'

    class Meta:
        verbose_name = 'Покупателя'
        verbose_name_plural = 'Покупатели'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, verbose_name='Покупатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    is_completed = models.BooleanField(default=False, verbose_name='Статус заказа')
    payment = models.BooleanField(default=False, verbose_name='Статус оплаты')
    shipping = models.BooleanField(default=True, verbose_name='Доставка')

    def __str__(self):
        return f'Номер заказа: {self.pk}, на имя {self.customer}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    @property
    def get_order_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([i.get_total_price for i in order_products])
        return total_price

    @property
    def get_order_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([i.quantity for i in order_products])
        return total_quantity



class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, verbose_name='Товар')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, verbose_name='Заказ')
    quantity = models.IntegerField(default=0, verbose_name='В количестве')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавление')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменение')

    def __str__(self):
        return f'Товар {self.product.title} по заказу: {self.order}'

    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'

    @property
    def get_total_price(self):
        if self.product.discount:
            percent = (self.product.price * self.product.discount) / 100
            self.product.price -= percent

        return self.product.price * self.quantity


    def total_price(self):
        return self.product.price * self.quantity


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, verbose_name='Покупатель')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, verbose_name='Заказ')
    address = models.CharField(max_length=150, verbose_name='Адрес доставки (улица, домб кв)')
    phone = models.CharField(max_length=30, verbose_name='Номер телефона')
    comment = models.TextField(verbose_name='Комментарий к заказу', max_length=150)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оформление заказа')
    region = models.ForeignKey('Region', on_delete=models.SET_NULL, null=True, verbose_name='Регион')
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, verbose_name='Город')

    def __str__(self):
        return f'Доствака для {self.customer.user.username.capitalize()}. На заказ: {self.order.pk}'

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставок'


class Region(models.Model):
    title = models.CharField(max_length=150, verbose_name='Регион')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'

class City(models.Model):
    title = models.CharField(max_length=150, verbose_name='Город')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион', related_name='cities')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

class SupportMessage(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True, verbose_name='Тема отзыва')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Никнейм пользователя')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Номер телефона')
    content = models.TextField(verbose_name='Контент отзыва')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')

    def __str__(self):
        return self.title if self.title else f"Отзыв от {self.user}"

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]


class Reviews(models.Model):
    text = models.CharField(max_length=200, verbose_name='Комментарий')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, default='user', verbose_name='Автор комментария')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавление')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменение')


    def __str__(self):
        return f'{self.user} на товар {self.product.title}'

    class Meta:
        verbose_name = 'Отзыв на товар'
        verbose_name_plural = 'Отзывы на товары'


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

# class Reviewer(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
#     review_amount = models.IntegerField(default=0, verbose_name='Количество комментарий')
#     rank = models.TextField(default='Начинающий', verbose_name='Ранк')
#
#     def __str__(self):
#         return f'{self.user.username} количество комментов: {self.review_amount}'
#
#     class Meta:
#         verbose_name = 'Ревьювер'
#         verbose_name_plural = 'Ревьюверы'
#
#     def update_review_count(self):
#         self.review_amount = Reviews.objects.filter(user=self.user).count()
#         self.save()
#
#     def update_rank(self):
#         if self.review_amount >= 10:
#             self.rank = 'Эксперт'
#         elif self.review_amount >= 5:
#             self.rank = 'Продвинутый'
#         else:
#             self.rank = 'Начинающий'
#         self.save()
#
#     def update_reviewer_status(self):
#         self.update_review_count()
#         self.update_rank()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    avatars = models.ImageField(upload_to='avatars/', verbose_name='Фото', null=True, blank=True)
    address = models.CharField(max_length=150, default='Не указан', verbose_name='Адрес доставки (улица, домб кв)')
    phone = models.CharField(max_length=30, default='Не указан', verbose_name='Номер телефона')
    region = models.CharField(max_length=30, default='Не указан', verbose_name='Регион')
    city = models.CharField(max_length=30, default='Не указан', verbose_name='Город')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def get_avatar(self):
        if self.avatars:
            return self.avatars.url
        else:
            return 'https://azimhakimschool.edu.bd/uploads/posts/08-07-2019_5d23043f9610b.png'


class RatingStar(models.Model):
    value = models.SmallIntegerField(default=0, verbose_name='Значение')

    def __str__(self):
        return f'{self.value}'

    class Meta:
        verbose_name = 'Звезду рейтинга'
        verbose_name_plural = 'Звезды рейтинга'
        ordering = ['value']


class ProductRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    star = models.ForeignKey(RatingStar, on_delete=models.CASCADE, verbose_name='Звезда')

    class Meta:
        verbose_name = 'Рейтинг Товара'
        verbose_name_plural = 'Рейтинги Товаров'
        unique_together = ('product', 'user')
        ordering = ['-id']

    def __str__(self):
        return f"Rating: {self.star.value} by {self.user.username} for {self.product}"

