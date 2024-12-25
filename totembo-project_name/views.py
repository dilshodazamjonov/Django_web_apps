from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.urls import reverse_lazy
from django.utils.timezone import now

from .models import *
from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from .forms import *
from django.contrib import messages
from .utils import CartForAuthenticatedUser, get_cart_data
from clocks.settings import STRIPE_SECRET_KEY
import stripe


# Create your views here.

class ProductListView(ListView):
    model = Product
    context_object_name = 'categories'
    template_name = 'totembo/index.html'
    extra_context = {
        'title': 'TOTEMBO',
    }

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)

        return categories


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        products = Product.objects.filter(category=product.category).exclude(slug=product.slug)
        # products = [i for i in products if i != product]
        context['title'] = product.title
        context['products'] = products
        context['comments'] = Reviews.objects.filter(product=product.pk)
        if self.request.user.is_authenticated:
            product_rating = ProductRating.objects.filter(user=self.request.user, product=product).first()
            if product_rating:
                context['existing_rating'] = product_rating


        if self.request.user.is_authenticated:
            context['comment_form'] = ReviewForm()
        return context


class ProductByCategory(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'totembo/category_page.html'
    paginate_by = 2

    def get_queryset(self):
        sub = self.request.GET.get('sub')
        color = self.request.GET.get('color')
        model = self.request.GET.get('model')
        price_from = self.request.GET.get('from')
        price_till = self.request.GET.get('till')

        category = Category.objects.get(slug=self.kwargs['slug'])
        subcategories = category.subcategories.all()
        products = Product.objects.filter(category__in=subcategories)

        if sub:
            products = products.filter(category__title=sub)
        if color:
            products = products.filter(color=color)
        if model:
            products = products.filter(model__title=model)
        if price_from:
            products = [i for i in products if int(i.price) >= int(price_from)]
        if price_till:
            products = [i for i in products if int(i.price) <= int(price_till)]

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(slug=self.kwargs['slug'])
        context['category'] = category.title
        subcategories = category.subcategories.all()
        products = Product.objects.filter(category__in=subcategories)
        context['colors'] = list(set([i.color for i in products]))
        context['models'] = list(set([i.model for i in products]))
        context['price_from'] = [i for i in range(0, 1100, 100)]
        context['price_till'] = [i for i in range(0, 5500, 500)]
        context['subcategories'] = subcategories
        # context['sub'] = self.request.GET.get('sub')
        # context['color'] = self.request.GET.get('color')
        # context['model'] = self.request.GET.get('model')
        # context['price_from'] = self.request.GET.get('from')
        # context['price_till'] = self.request.GET.get('till')

        context['query'] = self.request.GET
        return context


def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('main')
    else:
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                if user:
                    login(request, user)
                    messages.success(request, f'Добро пожаловать в Тотембо!, {user.username}')
                    return redirect('main')
                else:
                    messages.error(request, 'Вы ввели неверный логин или пароль')
                    return redirect('login')
            else:
                messages.error(request, 'Вы ввели неверный логин или пароль')
                return redirect('login')
        else:
            form = LoginForm()

        context = {
            'title': 'Авторизация',
            'login_form': form
        }
        return render(request, 'totembo/login.html', context)


def user_logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.warning(request, 'Вы успешно вышли из аккаунта.')
        return redirect('main')
    else:
        return redirect('main')


def user_registration_view(request):
    if request.user.is_authenticated:
        return redirect('main')
    else:
        if request.method == 'POST':
            form = RegistrationForm(data=request.POST)
            if form.is_valid():
                user = form.save()
                profile = Profile.objects.create(user=user)
                profile.save()
                messages.success(request, 'Ваш аккаунт был создан успешно')
                return redirect('login')
            else:
                for field in form.errors:
                    messages.error(request, form.errors[field].as_text())
                return redirect('register')
        else:
            form = RegistrationForm()

        context = {
            'title': 'Регистрация',
            'register_form': form
        }
        return render(request, 'totembo/registration.html', context)


def save_favorite_product_view(request, slug):
    if not request.user.is_authenticated:
        messages.warning(request, f'Войдите на аккаунт чтобы добавить в избранные.')
        return redirect('login')
    else:
        user = request.user
        product = Product.objects.get(slug=slug)
        favorite_products = FavoriteProduct.objects.filter(user=user)
        if user:
            if product in [i.product for i in favorite_products]:
                fav_products = FavoriteProduct.objects.get(product=product, user=user)
                fav_products.delete()
                messages.warning(request, f'Товар {product} был успешно удален из избранного')
                print(fav_products)
            else:
                FavoriteProduct.objects.create(product=product, user=user)
                messages.success(request, f'Товар {product} успешно был добавлен на избранные')

        next_page = request.META.get('HTTP_REFERER', 'main')
        return redirect(next_page)


class FavouriteListView(LoginRequiredMixin, ListView):
    model = FavoriteProduct
    context_object_name = 'product'
    template_name = 'totembo/favorite.html'
    login_url = reverse_lazy('login')

    extra_context = {
        'title': 'Моё избранное'
    }

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Войдите в аккаунт чтобы посмотреть избранные товары')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        favorites = FavoriteProduct.objects.filter(user=self.request.user)
        favorites = [i.product for i in favorites]
        context['favorites'] = favorites
        return context


class SalesProductListView(ListView):
    model = FavoriteProduct
    context_object_name = 'products'
    template_name = 'totembo/sales.html'
    login_url = 'login'
    extra_context = {
        'title': 'Товары по акции'
    }

    def get_queryset(self):
        products = Product.objects.all()
        products = [i for i in products if i.discount]
        return products


# view for adding a product into basket and deleting

def add_product_order(request, slug, action):
    product = Product.objects.get(slug=slug)
    if not request.user.is_authenticated:
        messages.error(request, 'Войдите в аккаунт чтобы добавить в корзину')
        return redirect('login')

    CartForAuthenticatedUser(request, slug, action)

    next = request.META.get('HTTP_REFERER', 'main')
    return redirect(next)


def my_cart_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Войдите в аккаунт чтобы посмотреть товары на вашей корзине')
        return redirect('login')

    else:
        order_info = get_cart_data(request)
        order_products = order_info['order_products']
        context = {
            'title': 'Ваша корзина',
            'order': order_info['order'],
            'order_products': order_products
        }
        return render(request, 'totembo/my_cart.html', context)


def delete_order_view(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'Авторизуйтесь чтобы удалить из корзины.')
        return redirect('login')
    else:
        order = Order.objects.get(pk=pk)
        order.delete()
        messages.success(request, 'Корзина успешно очищена')
        return redirect('my_cart')


def contact(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Войдите в аккаунт, чтобы написать в службу поддержки.')
        return redirect('login')

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_instance = form.save(commit=False)
            contact_instance.user = request.user  # Associate contact with the current user
            contact_instance.save()
            messages.success(request, 'Отзыв успешно отправлен. Менеджер скоро свяжется с вами.')
            return redirect(request.META.get('HTTP_REFERER', 'main'))
        else:
            messages.error(request, 'У вас есть незаполненные или некорректные поля.')
    else:
        form = ContactForm()

    context = {
        'title': 'Служба поддержки',
        'contact_form': form
    }
    return render(request, 'totembo/contact_page.html', context)


def save_comment(request, slug):
    if request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = Product.objects.get(slug=slug)
            messages.success(request, 'Ваш комментарий успешно был добавлен!')
            comment.save()
            return redirect('product', slug)
    else:
        return redirect('main')


# def update_comment(request, pk):
#     if not request.user.is_authenticated:
#         messages.error(request, 'Войдите в аккаунт чтобы продолжить')
#         return redirect('login')
#
#     try:
#         comment = Reviews.objects.get(pk=pk, user=request.user)
#     except Reviews.DoesNotExist:
#         messages.error(request, 'Комментарий не найден или вы не имеете прав для его редактирования.')
#         return redirect('main')
#
#     if request.method == 'POST':
#         form = ReviewForm(request.POST, instance=comment)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Комментарий успешно обновлен.')
#             return redirect('product', pk=comment.product.pk)
#         else:
#             messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
#     else:
#         form = ReviewForm(instance=comment)
#
#     context = {
#         'form': form,
#         'comment': comment,
#         'product': comment.product,
#     }
#
#     return render(request, 'product_detail.html', context)


def comment_delete(request, comment_pk, product_pk):
    user = request.user if request.user.is_authenticated else None
    comment = Reviews.objects.get(pk=comment_pk, product_id=product_pk)
    if user:
        if comment.user == request.user:
            product = Product.objects.get(pk=product_pk)
            comment.delete()
            messages.success(request, 'Ваш комментарий был успешно удален!')
            return redirect('product', product.slug)
        else:
            messages.error(request, 'Такой комментарий не найден😢')
            return redirect('login')
    else:
        messages.error(request, 'Войдите в аккаунт')
        return redirect('login')


def edit_comment(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        comment_text = request.POST.get('comment_text')
        comment = get_object_or_404(Reviews, pk=comment_id, user=request.user)
        comment.text = comment_text
        comment.save()
        messages.success(request, 'Ваш комментарий успешно изменен')
        return redirect('product', slug=comment.product.slug)


def checkout_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Авторизуйтесь чтобы оформлять заказ')
        return redirect('login')
    else:
        order_info = get_cart_data(request)
        if order_info['order_products']:
            regions = Region.objects.all()
            dict_city = {i.pk: [[j.title, j.pk] for j in i.cities.all()] for i in regions}
            context = {
                'title': 'Оформление заказа',
                'order': order_info['order'],
                'items': order_info['order_products'],
                'shipping_form': ShippingForm(),
                'dict_city': dict_city
            }
            return render(request, 'totembo/checkout.html', context)
        else:
            next_page = request.META.get('HTTP_REFERER', 'main')
            return redirect(next_page)


def create_checkout_session_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Авторизуйтесь чтобы продолжить')
        return redirect('login')

    else:
        stripe.api_key = STRIPE_SECRET_KEY
        if request.method == 'POST':
            order_info = get_cart_data(request)
            shipping_form = ShippingForm(data=request.POST)
            ship_address = ShippingAddress.objects.all()

            if shipping_form.is_valid():
                shipping = shipping_form.save(commit=False)
                shipping.customer = Customer.objects.get(user=request.user)
                shipping.order = order_info['order']
                if order_info['order'] not in [i for i in ship_address]:
                    shipping.save()
            else:
                return redirect('checkout')

            order_price = order_info['order_total_price']
            session = stripe.checkout.Session.create(
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'Товары магазина Totembo'},
                        'unit_amount': int(order_price) * 100
                    },
                    'quantity': 1
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('success')),
                cancel_url=request.build_absolute_uri(reverse('checkout')),
            )

            return redirect(session.url, 303)


def success_payment(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Авторизуйтесь чтобы продолжить')
        return redirect('login')
    else:
        cart = CartForAuthenticatedUser(request)
        next_page = request.META.get('HTTP_REFERER', 'main')
        cart.clear_cart()

        context = {
            'title': 'Успешная оплата',
        }
        return render(request, 'totembo/success.html', context)


def product_search(request):
    word = request.GET.get('q', '')
    if word:
        products = Product.objects.filter(title__icontains=word)
    else:
        products = Product.objects.all()
    length_of = len(products)
    context = {
        'title_body': word,
        'title': 'Результаты поиска',
        'products': products,
        'quantity': length_of
    }
    return render(request, 'totembo/product_search_results.html', context)


class PrivacyPolicyView(TemplateView):
    template_name = 'totembo/privacy.html'


def subscribe(request):
    # Get the previous page URL to redirect back after submission
    next_page = request.META.get('HTTP_REFERER', 'main')

    if request.method == 'POST':
        email = request.POST.get('email')

        if email:
            subscriber, created = Subscriber.objects.update_or_create(
                email=email,
                defaults={'subscribed_at': now()}
            )

            if created:
                messages.success(request, 'Спасибо за подписку!')
            else:
                messages.error(request, 'Ваш адрес электронной почты уже зарегистрирован, обновлена дата подписки.')
        else:
            messages.error(request, 'Пожалуйста, введите корректный адрес электронной почты.')

    return redirect(next_page)


def profile_view(request):
    user = request.user if request.user.is_authenticated else None
    if user:
        profile = Profile.objects.get(user=user)
        comments = Reviews.objects.filter(user=user)
        count_comments = len(comments)

        # Get the most recent order with payment=True, if it exists
        order = Order.objects.filter(customer__user=user, payment=True).order_by('-id').first()
        items = OrderProduct.objects.filter(order=order) if order else []

        context = {
            'title': f'Профиль {user}',
            'profile': profile,
            'count': count_comments,
            'order': order,
            'items': items
        }

        return render(request, 'totembo/profile.html', context)

    else:
        messages.error(request, 'Авторизуйтесь чтобы продолжить')
        return redirect('login')


def edit_account_profile_view(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        if profile:
            account_form = EditAccountForm(instance=request.user)
            profile_form = EditProfileForm(instance=request.user.profile)

            context = {
                'title': f'Изменения данных {request.user.username}',
                'account_form': account_form,
                'profile_form': profile_form
            }
            return render(request, 'totembo/edit_account.html', context)
        else:
            messages.error(request, 'Авторизуйтесь чтобы продолжить')
            return redirect('login')
    else:
        messages.error(request, 'Авторизуйтесь чтобы продолжить')
        return redirect('login')


def edit_profile_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Авторизуйтесь чтобы продолжить')
        return redirect('login')
    else:
        if request.method == 'POST':
            edit_profile = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
            if edit_profile.is_valid():
                edit_profile.save()
                messages.success(request, 'Данные изменены')
                return redirect('profile')
            else:
                messages.error(request, 'Вы указали не корректные данные')
                return redirect('change')

# def edit_account_view(request):
#     if not request.user.is_authenticated:
#         return redirect('login')
#     else:
#         if request.method == 'POST':
#             edit_account_form = EditAccountForm(request.POST, instance=request.user)
#             if edit_account_form.is_valid():
#                 edit_account_form.save()
#                 data = edit_account_form.cleaned_data
#                 user = User.objects.get(id=request.user.id)
#                 if user.check_password(data['old_password']):
#                     if not user.check_password(data['old_password']):
#                         messages.error(request, 'Неверный текущий пароль')
#                         return redirect('change')
#                     if data['new_password'] != data['confirm_password']:
#                         messages.error(request, 'Новые пароли не совпадают')
#                         return redirect('change')
#                     if data['old_password'] and data['new_password'] == data['confirm_password']:
#                         user.set_password(data['new_password'])
#                         user.save()
#                         update_session_auth_hash(request, user)
#                         messages.success(request, 'Данные успешно изменены')
#                         return redirect('profile')
#                 else:
#                     for field in edit_account_form.errors:
#                         messages.error(request, edit_account_form.errors[field].as_text())
#                         return redirect('change')
#
#                 return redirect('profile')
#
#             else:
#                 for field in edit_account_form.errors:
#                     messages.error(request, edit_account_form.errors[field].as_text())
#                     return redirect('change')


def edit_account_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Авторизуйтесь чтобы продолжить')
        return redirect('login')

    if request.method == 'POST':
        edit_account_form = EditAccountForm(request.POST, instance=request.user)

        if edit_account_form.is_valid():
            data = edit_account_form.cleaned_data
            user = request.user

            if not user.check_password(data['old_password']):
                messages.error(request, 'Неверный текущий пароль')
                return redirect('change')

            if data['new_password'] and data['new_password'] != data['confirm_password']:
                messages.error(request, 'Новые пароли не совпадают')
                return redirect('change')

            # Save the new password if provided
            if data['new_password']:
                user.set_password(data['new_password'])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль успешно изменен')

            edit_account_form.save()
            messages.success(request, 'Данные успешно обновлены')
            return redirect('profile')

        else:
            for field, errors in edit_account_form.errors.items():
                messages.error(request, f"{field}: {errors.as_text()}")
            return redirect('change')


    else:
        messages.error(request, 'Метод запроса не POST')
        return redirect('main')


def rate_product(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        if not request.user.is_authenticated:
            messages.error(request, "Вы должны быть авторизованы, чтобы оценить товар.")
            return redirect('product', slug=product.slug)

        try:
            star_value = int(request.POST.get('rating', 0))
            if star_value < 1 or star_value > 5:
                raise ValueError("Invalid rating value")
        except (ValueError, TypeError):
            messages.error(request, "Недопустимое значение оценки.")
            return redirect('product', slug=product.slug)

        star = get_object_or_404(RatingStar, value=star_value)


        existing_rating = ProductRating.objects.filter(product=product, user=request.user).first()

        if existing_rating:
            existing_rating.star = star
            existing_rating.save()
        else:

            ProductRating.objects.create(
                product=product,
                user=request.user,
                star=star
            )

        avg_rating = product.ratings.aggregate(Avg('star__value'))['star__value__avg']
        product.average_rating = avg_rating or 0
        product.save()


        messages.success(
            request,
            f"Спасибо за вашу оценку! Новая средняя оценка: {product.average_rating:.1f}."
        )
        context = {
            'existing_rating': existing_rating
        }
        return redirect('product', slug=product.slug)







# def rate_product(request, product_id):
#     if request.method == 'POST':
#         try:
#             # Get the product object
#             product = Product.objects.get(id=product_id)
#
#             # Get rating value from the form (assumed to be 1-5)
#             data = json.loads(request.body)
#             rating_value = int(data.get('rating', 0))
#
#             # Validate rating value
#             if rating_value < 1 or rating_value > 5:
#                 return JsonResponse({'error': 'Неверная оценка.'}, status=400)
#
#             # Get or create the rating star object
#             rating_star = RatingStar.objects.get(value=rating_value)
#
#             # Update or create a new ProductRating
#             product_rating, created = ProductRating.objects.update_or_create(
#                 product=product,
#                 user=request.user,
#                 defaults={'star': rating_star}
#             )
#
#             # Recalculate the average rating for the product
#             avg_rating = ProductRating.objects.filter(product=product).aggregate(Avg('star__value'))['star__value__avg']
#             avg_rating = round(avg_rating, 1) if avg_rating else 0
#
#             product.average_rating = avg_rating
#             product.save()
#             return JsonResponse({'message': f'Спасибо за вашу оценку! Средняя оценка: {avg_rating}'})
#
#         except Product.DoesNotExist:
#             messages.error(request, 'Товар не найден.')
#             return redirect('product', slug=product.slug)
#
#     return JsonResponse({'error': 'Неверный метод запроса.'}, status=405)





# ==================================== Profile View ========================================

# def profile_view(request):
#     if not request.user.is_authenticated:
#         messages.error(request, 'Авторизуйтесь чтобы продолжить')
#         return redirect('login')
#
#     account_form = EditAccountForm(instance=request.user)
#     profile_form = EditProfileForm(instance=getattr(request.user, 'profile', None))
#     orders = None  # Default value in case no orders are found
#
#     if request.method == 'POST':
#         account_form = EditAccountForm(request.POST, instance=request.user)
#         profile_form = EditProfileForm(request.POST, instance=getattr(request.user, 'profile', None))
#         if account_form.is_valid() and profile_form.is_valid():
#             account_form.save()
#             profile_form.save()
#             messages.success(request, 'Ваш профиль обновлён успешно.')
#             return redirect('profile')
#         else:
#             messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
#
#     try:
#         customer = Customer.objects.get(user=request.user)
#         orders = Order.objects.filter(customer=customer, payment=True)
#     except Customer.DoesNotExist:
#         messages.warning(request, 'Связанный клиент не найден. Заказы недоступны.')
#     except Exception as e:
#         messages.error(request, f'Ошибка при загрузке заказов: {e}')
#
#     context = {
#         'title': f'Профиль {request.user}',
#         'account_form': account_form,
#         'profile_form': profile_form,
#         'orders': orders[::-1][:1],
#     }
#     return render(request, 'totembo/profile.html', context)
