from django import forms

from .models import FeatureValidator, CategoryFeature
from Shop.models import Category, Brand, Order, Product


class NewCategoryFeatureKeyForm(forms.ModelForm):

    class Meta:
        model = CategoryFeature
        fields = '__all__'


class NewCategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = '__all__'

class NewProductForm(forms.ModelForm):

    # title = forms.CharField(required=True)
    # slug = forms.CharField(required=True)
    # amount = forms.IntegerField(required=True, max_value=100000, min_value=0)
    # description = forms.CharField(required=True)
    # price = forms.FloatField(required=True, max_value=1000000, min_value=0)
    # old_price = forms.FloatField(required=True, max_value=1000000, min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields =  '__all__'
    

class NewBrandForm(forms.ModelForm):

    class Meta:
        model = Brand
        fields = '__all__'


class FeatureValidatorForm(forms.ModelForm):

    class Meta:
        model = FeatureValidator
        fields = ['category']


class EditOrderStatusForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['status']