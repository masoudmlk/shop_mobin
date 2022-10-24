from django_filters.rest_framework import FilterSet
from core.models import Product


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'type': ['exact'],
            'name': ['icontains'],
            'brand': ['icontains'],
        }