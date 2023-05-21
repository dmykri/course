from itertools import product
from pydoc import describe
from unicodedata import category
from django.test import TestCase
from Shop.models import Brand, Category, Customer, Product, User
from django.contrib.auth import get_user_model
import tempfile

class NewCategoryCase(TestCase):
    def setUp(self):
        Category.objects.create(name="Smartphones", slug="smartphones")
        Category.objects.create(name="Notebooks", slug="notebooks")

    def test_order(self):

        smartphones = Category.objects.get(name="Smartphones")
        notebooks = Category.objects.get(name="Notebooks")
        self.assertEqual(smartphones.slug, 'smartphones')
        self.assertEqual(notebooks.slug, 'notebooks')

class NewCustomerCase(TestCase):
    def setUp(self):
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')  
        user.is_staff=False 
        user.save()
        customer = Customer.objects.create(user=user, phone='007007007', address='Dnipro')
        customer.save()

    def test_customer(self):

        customer = Customer.objects.get(phone='007007007')
        user = User.objects.get(email='lennon@thebeatles.com')
        self.assertEqual(customer.user, user)

class NewProductCase(TestCase):
    def setUp(self):
        image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        smartphones = Category.objects.create(name="Smartphones", slug="smartphones")
        google = Brand.objects.create(slug='google', brand_text='Google', email='google@google.com', phone='11111111', top_brand=True)
        Product.objects.create(brand=google, category=smartphones, image=image, title='Pixel 6', slug='pxl6', description='test phone', amount=10, old_price=0, price=600)

    def test_customer(self):

        product = Product.objects.get(title='Pixel 6')
        category = Category.objects.get(slug='smartphones')
        brand = Brand.objects.get(slug='google')
        self.assertEqual(product.category, category)
        self.assertEqual(product.brand, brand)