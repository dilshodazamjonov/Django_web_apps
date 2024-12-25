from django import forms
from .models import *
from django_svg_image_form_field import SvgAndImageFormField
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = []
        field_classes = {
            'icon': SvgAndImageFormField
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Логин'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Пароль'
    }))

    class Meta:
        model = User
        fields = ('username', 'password')


class RegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Логин'
    }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваше имя'
    }), required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваше фамилия'
    }), required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Почтовый адрес'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите пароль'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Повторите пароль'
    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class ContactForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Тема отзыва'
    }))
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control contact_textarea',
        'placeholder': 'Контент отзыва'
    }))
    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Номер телефона или телеграм'
    }))

    class Meta:
        model = SupportMessage
        fields = ('phone', 'title', 'content')
        labels = {
            'phone': '',
            'title': '',
            'content': '',
        }


class ReviewForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control_comment',
        'placeholder': 'Ваш отзыв про товар'
    }))

    class Meta:
        model = Reviews
        fields = ('text',)
        labels = {
            'text': ''
        }


class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ('address', 'phone', 'region', 'city', 'comment')
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'form-control_checkout',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control_checkout',
            }),
            'region': forms.Select(attrs={
                'class': 'form_control_checkout',
            }),
            'city': forms.Select(attrs={
                'class': 'form_control_checkout',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form_control_checkout',
            })

        }

class EditAccountForm(UserChangeForm):
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control_profile'
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control_profile'
    }))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={
        'class': 'form-control_profile'
    }))
    old_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={
        'class': 'form-control_profile'
    }))
    new_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={
        'class': 'form-control_profile'
    }))
    confirm_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={
        'class': 'form-control_profile'
    }))
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'old_password', 'new_password', 'confirm_password')


class EditProfileForm(forms.ModelForm):
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control_profile'
    }))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control_profile'
    }))
    avatars = forms.FileField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control_profile'
    }))
    region = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control_profile'
    }))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control_profile'
    }))

    class Meta:
        model = Profile
        fields = ('avatars', 'phone', 'address', 'region', 'city')

