from django import forms
from django.contrib.contenttypes import fields
from django.core.exceptions import ValidationError
from django.forms.fields import EmailField
from django.forms.formsets import formset_factory
from .models import Order, Customer
from django.contrib.auth.models import User

class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

    class Meta:
        model = Order
        fields = (
            'first_name', 'last_name', 'phone', 'address', 'buying_type', 'comment'
        )


class LoginForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            'username', 'password'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логін'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Користувача з логіном {username} не знайдено в системі!')
        user = User.objects.filter(username=username).first()
        if not user.check_password(password):
            raise forms.ValidationError(f'Пароль не вірний!')
        return self.cleaned_data


class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(required=False)
    address = forms.CharField(required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username', 'password', 'confirm_password', 'email', 'first_name', 'last_name', 'phone', 'address'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логін'
        self.fields['password'].label = 'Пароль'
        self.fields['confirm_password'].label = 'Повторіть пароль'
        self.fields['email'].label = 'Ел. пошта'
        self.fields['first_name'].label = 'Імя'
        self.fields['last_name'].label = 'Прізвище'
        self.fields['phone'].label = 'Номер телефону'
        self.fields['address'].label = 'Адреса'


    def clean_email(self):
        
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'Ця електронна адреса вже використовується!')

        return email

    def clean_username(self):

        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Логін {username} вже зайнято!')

        return username

    def clean(self):

        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if password != confirm_password:
            raise forms.ValidationError(f'Паролі не збігаються!')

        return self.cleaned_data

class EditCustomerForm(forms.ModelForm):
    phone = forms.CharField(required=False)
    address = forms.CharField(required=False)
        

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone', 'address'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Імя'
        self.fields['last_name'].label = 'Прізвище'
        self.fields['phone'].label = 'Номер телефону'
        self.fields['address'].label = 'Адреса'
    
    