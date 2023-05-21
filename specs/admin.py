from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(ProductFeatures)
admin.site.register(CategoryFeature)
admin.site.register(FeatureValidator)