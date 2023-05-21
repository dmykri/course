from enum import unique
from django.db import models

from Shop.models import Category



class CategoryFeature(models.Model):

    category = models.ForeignKey('Shop.Category', verbose_name='Категорія', on_delete=models.CASCADE)
    feature_name = models.CharField(max_length=100, verbose_name='Назва характеристики')
    feature_filter_name = models.CharField(max_length=50, verbose_name='Назва для фільтру')
    unit = models.CharField(max_length=20, verbose_name='Один. вимірювання', null=True, blank=True)

    class Meta:
        unique_together = ('category', 'feature_name', 'feature_filter_name')
        verbose_name = 'Характеристика категорії'
        verbose_name_plural = 'Характеристики категорії'

    def __str__(self):
        return f"{self.category.name} | {self.feature_name}"


class FeatureValidator(models.Model):

    category = models.ForeignKey('Shop.Category', verbose_name='Категорія', on_delete=models.CASCADE)
    feature_key = models.ForeignKey(CategoryFeature, verbose_name='Ключ характеристики', on_delete=models.CASCADE)
    valid_feature_value = models.CharField(max_length=100, verbose_name='Валідне значення')

    def __str__(self):
        return f"Категорія {self.category.name} | Характеристика {self.feature_key.feature_name} | Валідне значення {self.valid_feature_value}"
    
    class Meta:
        verbose_name = 'Значення характеристик'
        verbose_name_plural = 'Усі значення характеристик'

class ProductFeatures(models.Model):

    product = models.ForeignKey('Shop.Product', verbose_name='Товар', on_delete=models.CASCADE)
    feature = models.ForeignKey(CategoryFeature, verbose_name='Характеристика', on_delete=models.CASCADE)
    value = models.CharField(max_length=100, verbose_name='Значення')

    def __str__(self):
        return f"Товар {self.product.title} | Характеристика {self.feature.feature_name} | Значення {self.value}"

    class Meta:
        verbose_name = 'Характиристики продукта'
        verbose_name_plural = 'Характиристики продуктів'
