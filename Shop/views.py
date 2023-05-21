from itertools import product
from django.contrib import auth
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import DetailView, View
from django.http import HttpResponseRedirect
from .models import *
from .mixins import CartMixin, CategoryDetailMixin
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import OrderForm, LoginForm, RegistrationForm, EditCustomerForm
from .utils import recalc_cart, amount_check
from django.db import transaction

from django.utils.decorators import method_decorator

from specs.models import ProductFeatures


class MyQ(Q):

    default = 'OR'

class BaseView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        products = Product.objects.filter(amount__gt=0).order_by('-id')[:16]
        top_brands = Brand.objects.filter(top_brand=True)
        context={
            'categories': categories,
            'products': products,
            'cart': self.cart,
            'top_brands': top_brands
        }
        return render(request, 'base.html', context)

class EditCustomerView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        user = request.user
        customer = Customer.objects.get(user=user)
        form = EditCustomerForm(request.POST or None)
        if form.is_valid():
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()
                customer.phone = form.cleaned_data['phone']
                customer.address = form.cleaned_data['address']
                customer.save()
                messages.add_message(request, messages.WARNING, 'Успішно!')
                return HttpResponseRedirect('/profile/')
        messages.add_message(request, messages.WARNING, 'Сталася помилка!')
        return HttpResponseRedirect('/profile/')

class ProductDetailView(CartMixin, DetailView):

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'
    
    def dispatch(self, request, *args, **kwargs):

        self.model = Product
        self.queryset = Product.objects.all()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        context['categories'] = Category.objects.all()
        return context


class AddToCartView(LoginRequiredMixin, CartMixin, View):

    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        if product.amount > 0:
            cart_product, created= CartProduct.objects.get_or_create(user=self.cart.owner, cart=self.cart, product=product)
            if created:
                self.cart.products.add(cart_product)
                messages.add_message(request, messages.INFO, "Товар успішно додано!")
        else:
            messages.add_message(request, messages.INFO, "Вибачте, але товару немає в наявності!")
        recalc_cart(self.cart)
        return HttpResponseRedirect('/cart/')

class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product= CartProduct.objects.get(user=self.cart.owner, cart=self.cart, product=product)
        self.cart.products.remove(cart_product)
        cart_product.delete()
        messages.add_message(request, messages.INFO, "Товар успішно видалено!")
        recalc_cart(self.cart)
        return HttpResponseRedirect('/cart/')

class CategoryDetailView(CartMixin, DetailView):

    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('search')
        category = self.get_object()
        context['cart'] = self.cart
        context['categories'] = self.model.objects.all()
        if not query and not self.request.GET:
            context['category_products'] = category.product_set.all()
            return context
        if query:
            products = category.product_set.filter(Q(title__icontains=query))
            context['category_products'] = products
            return context
        url_kwargs = {}
        for item in self.request.GET:
            if len(self.request.GET.getlist(item)) > 1:
                url_kwargs[item] = self.request.GET.getlist(item)
            else:
                url_kwargs[item] = self.request.GET.get(item)
        q_condition_queries = Q()
        for key, value in url_kwargs.items():
            if isinstance(value, list):
                q_condition_queries.add(Q(**{'value__in': value}), Q.OR)
            else:
                q_condition_queries.add(Q(**{'value': value}), Q.OR)
        pf = ProductFeatures.objects.filter(
            q_condition_queries
        ).prefetch_related('product', 'feature').values('product_id')
        products = Product.objects.filter(id__in=[pf_['product_id'] for pf_ in pf], category=self.get_object())
        context['category_products'] = products
        return context

class ChangeQTYView(CartMixin, View):


    def post(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product= CartProduct.objects.get(user=self.cart.owner, cart=self.cart, product=product)
        qty = int(request.POST.get('qty'))
        if product.amount >= qty:
            cart_product.qty = qty
            cart_product.save()
            recalc_cart(self.cart)
            messages.add_message(request, messages.INFO, "Кількість товару змінено!")
            print(request.POST)
            return HttpResponseRedirect('/cart/')
        else:
            text = "Нажаль, ми не маємо на даний момент таку кількість товару. Максимальна кількість " + product.title + " = " + str(product.amount) + " од."
            messages.add_message(request, messages.INFO, text)
            return HttpResponseRedirect('/cart/')

class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        context={
            'categories': categories,
            'cart': self.cart,
        }
        return render(request, 'cart.html', context)

class CheckoutView(OrderForm, CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        customer = Customer.objects.get(user=request.user)
        form = OrderForm(request.POST or None, initial={
            'first_name': customer.user.first_name,
            'last_name': customer.user.last_name,
            'phone': customer.phone,
            'address': customer.address
        })
        context={
            'categories': categories,
            'cart': self.cart,
            'form': form
        }
        return render(request, 'checkout.html', context)

class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            amount_flag = 0
            for cart_product in self.cart.products.all():
                product = cart_product.product
                if cart_product.qty > product.amount and product.amount != 0:
                    amount_flag += 1
                    text = "Максимальна кількість " + product.title + " = " + str(product.amount) + " од. Кількість в корзині змінено."
                    messages.add_message(request, messages.INFO, text)
                    cart_product.qty = product.amount
                    cart_product.save()
                    recalc_cart(self.cart)
                elif product.amount == 0:
                    amount_flag += 1
                    text = "Товару немає в наявності " + product.title
                    messages.add_message(request, messages.INFO, text)
                    self.cart.products.remove(cart_product)
                    cart_product.delete()
                    recalc_cart(self.cart)
            if amount_flag > 0:
                return HttpResponseRedirect('/checkout/')
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            for cart_product in self.cart.products.all():
                product = cart_product.product
                product.amount = product.amount - cart_product.qty
                product.save()
            self.cart.in_order = True
            self.cart.save()
            amount_check()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Дякуємо за замовлення! З вами зв\'яжеться менеджер')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout/')

class LoginView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        categories = Category.objects.all()
        context = {
            'form': form,
            'categories': categories,
            "cart": self.cart
        }
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password'] 
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')

        context = {
            'form': form, 
            'cart': self.cart
            }
        return render(request, 'login.html', context)

class RegistrationView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        categories = Category.objects.all()
        context = {
            'form': form,
            'categories': categories,
            "cart": self.cart
        }
        return render(request, 'registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user, 
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'] 
                )

            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return HttpResponseRedirect('/')

        context = {
            'form': form, 
            'cart': self.cart
            }
        return render(request, 'registration.html', context)


class ProfileView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer).order_by('-created_at')
        categories = Category.objects.all()
        user = request.user
        edit_customer_form = EditCustomerForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': customer.phone,
            'address': customer.address
        })
        context={
            'edit_customer_form': edit_customer_form,
            'orders': orders,
            'categories': categories,
            'cart': self.cart,
        }
        return render(request, 'profile.html', context)



def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)


class BrandDetailView(CartMixin, DetailView):

    model = Brand
    queryset = Brand.objects.all()
    context_object_name = 'brand'
    template_name = 'brand_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = self.get_object()
        context['cart'] = self.cart
        context['categories'] = Category.objects.all()
        context['brand_products'] = Product.objects.filter(brand=brand)
        return context
