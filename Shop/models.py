import django
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()


class Brand(models.Model):
    slug = models.SlugField(unique=True)
    brand_text = models.CharField(max_length=30, verbose_name='Назва бренду')
    email = models.EmailField(verbose_name='Електронна пошта')
    phone = models.CharField(max_length=20, verbose_name='Номер телефону')
    top_brand = models.BooleanField(default=True, verbose_name='Топ бренд')

    def __str__(self):
        return self.brand_text

    def get_absolute_url(self):
        return reverse('brand_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренди'


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Імя категорії')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class Product(models.Model):

    category = models.ForeignKey(Category, verbose_name='Категорія', on_delete=models.CASCADE, default='notebook')
    brand = models.ForeignKey(Brand, verbose_name='Бренд', on_delete=models.CASCADE, default='')
    title = models.CharField(max_length=100, verbose_name='Назва товару', default='default')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Зображення', upload_to = "images/")
    description = models.TextField(verbose_name='Опис', null=True)
    amount = models.PositiveIntegerField(default=1, verbose_name='Кількість на складі', validators=[
        MaxValueValidator(
            limit_value = 100000,
            message = 'Не може бути більше 100 тисяч'
        ),
        MinValueValidator(
            limit_value=0,
            message = 'Кількість не може бути нижчою за 0!'
        )
    ])
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Ціна', validators=[
        MaxValueValidator(
            limit_value = 1000000,
            message = 'Ціна не може перевищувати 1 млн грн!'
        ),
        MinValueValidator(
            limit_value=0,
            message = 'Ціна не може бути нижчою за 0 гривень!'
        )
    ])
    old_price = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name='Стара ціна', validators=[
        MaxValueValidator(
            limit_value = 1000000,
            message = 'Ціна не може перевищувати 1 млн грн!'
        )
    ])
    features = models.ManyToManyField("specs.ProductFeatures", blank=True, related_name='features_for_product')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'

    def __str__(self):
        return "{} {}".format(self.brand.brand_text, self.title) 

    def get_model_name(self):
        return self.__class__.__name__.lower()

    def get_features(self):
        return {f.feature.feature_name: ' '.join([f.value, f.feature.unit or ""]) for f in self.features.all()}

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупець', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Кошик', on_delete=models.CASCADE, related_name='related_products')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Сумма')

    def __str__(self):
        return f'Продукт для кошика "{self.product.title}"'

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.product.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Продукт для корзини'
        verbose_name_plural = 'Продукти для корзини'

class Cart(models.Model):

    owner = models.ForeignKey('Customer', null=True, verbose_name='', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name='Сумма до оплати')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return f'Кошик "{self.id}"'


    class Meta:
        verbose_name = 'Кошик'
        verbose_name_plural = 'Кошики'


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Користувач', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефону', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Адреса', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Замовлення покупця', related_name ='related_customer')

    def __str__(self):
        return "Покупець {} {}".format(self.user.first_name, self.user.last_name)

    class Meta:
        verbose_name = 'Покупець'
        verbose_name_plural = 'Покупці'


class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'
    BUYING_TYPE_SHOP = 'shop'

    STATUS_CHOISES = (
        (STATUS_NEW, 'Нове замовлення'),
        (STATUS_IN_PROGRESS, 'Замовлення в процесі'),
        (STATUS_READY, 'Замовлення готове'),
        (STATUS_COMPLETED, 'Замовлення завершене')
    )

    BUYING_CHOISES = (
        (BUYING_TYPE_SELF,'Самовивіз'),
        (BUYING_TYPE_DELIVERY,'Доставка кур\'єром'),
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупець', related_name ='related_orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Імя')
    last_name = models.CharField(max_length=255, verbose_name='Прізвище')
    phone = models.CharField(max_length=20, verbose_name='Номер телефону')
    cart = models.ForeignKey(Cart, verbose_name='Кошик', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адреса', null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Статус замовлення', choices=STATUS_CHOISES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name='Тип замовлення', choices=BUYING_CHOISES, default=BUYING_TYPE_SELF)
    comment = models.TextField(verbose_name='Комментарій', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True,  verbose_name='Дата створення замовлення')
    order_date = models.DateField(verbose_name='Дата отримання замовлення', default=(date.today() + timedelta(days=2)))

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення (множина)'
