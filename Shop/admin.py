
from django.contrib import admin
from .models import *


admin.site.site_header = "Kryashop-admin"

class ProductAdmin(admin.ModelAdmin):
    change_form_template = 'custom_admin/change_form.html'
    #exclude = ('features',)

admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Customer)
admin.site.register(Brand)
admin.site.register(Order)
admin.site.register(Product)