from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import ProductItem, Product


@receiver(post_save, sender=Product)
def create_product_item(sender, **kwargs):
    if kwargs['created']:
        ProductItem.objects.create(product=kwargs['instance'], quantity=0)
