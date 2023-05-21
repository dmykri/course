from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from .views import (
    BaseSpecView,
    CompletedOrdersView,
    CreateNewBrand,
    CreateNewFeature,
    CreateNewCategory,
    CreateNewFeatureValidator,
    EditOrderStatusView,
    FeatureChoiceView,
    CreateFeatureView,
    InProgressOrdersView,
    NewOrdersView,
    NewProductFeatureView,
    OrdersView,
    ReadyOrdersView,
    SearchProductAjaxView,
    AttachNewFeatureToProduct,
    ProductFeatureChoicesAjaxView,
    CreateNewProductFeatureAjaxView,
    UpdateProductFeaturesView,
    ShowProductFeaturesForUpdate,
    UpdateProductFeaturesAjaxView,
    CreateNewProduct
)

urlpatterns = [
    path('', BaseSpecView.as_view(), name='product-list-for-features'),
    path('new-feature/', CreateNewFeature.as_view(), name='new-feature'),
    path('new-category/', CreateNewCategory.as_view(), name='new-category'),
    path('new-validator/', CreateNewFeatureValidator.as_view(), name='new-validator'),
    path('feature-choice/', FeatureChoiceView.as_view(), name='feature-choice-validators'),
    path('feature-create/', CreateFeatureView.as_view(), name='create-feature'),
    path('new-product-feature/', NewProductFeatureView.as_view(), name='new-product-feature'),
    path('search-product/', SearchProductAjaxView.as_view(), name='search-product'),
    path('attach-feature/', AttachNewFeatureToProduct.as_view(), name='attach-feature'),
    path('product-feature/', ProductFeatureChoicesAjaxView.as_view(), name='product-feature'),
    path('attach-new-product-feature/', CreateNewProductFeatureAjaxView.as_view(), name='attach-new-product-feature'),
    path('update-product-features/', UpdateProductFeaturesView.as_view(), name='update-product-features'),
    path('show-product-features-for-update/', ShowProductFeaturesForUpdate.as_view(), name='show-product-features-for-update'),
    path('update-product-features-ajax/', UpdateProductFeaturesAjaxView.as_view(), name='update-product-features-ajax'),
    path('new-brand/', CreateNewBrand.as_view(), name='new-brand'),
    path('new-product/', CreateNewProduct.as_view(), name='new-product'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('new-orders/', NewOrdersView.as_view(), name='new-orders'),
    path('ready-orders/', ReadyOrdersView.as_view(), name='ready-orders'),
    path('completed-orders/', CompletedOrdersView.as_view(), name='completed-orders'),
    path('in-progress-orders/', InProgressOrdersView.as_view(), name='in-progress-orders'),
    path('edit-order/<int:pk>', EditOrderStatusView.as_view(), name='edit-order'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
