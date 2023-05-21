
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings
from Shop.forms import LoginForm
from .views import AddToCartView, BaseView, BrandDetailView, CartView, LoginView, ProductDetailView, CategoryDetailView, DeleteFromCartView, ChangeQTYView, CheckoutView, MakeOrderView, ProfileView, RegistrationView, EditCustomerView


handler404 = "Shop.views.page_not_found_view"

urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('products/<str:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:slug>', AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<str:slug>', DeleteFromCartView.as_view(), name='delete_from_cart'),
    path('change-qty/<str:slug>', ChangeQTYView.as_view(), name='change_qty'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('make-order/', MakeOrderView.as_view(), name='make_order'),
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('logout/', LogoutView.as_view(next_page="/"), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit-customer/', EditCustomerView.as_view(), name='edit_customer'),
    path('brands/<str:slug>/', BrandDetailView.as_view(), name='brand_detail')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
