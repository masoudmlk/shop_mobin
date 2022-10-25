from django.contrib import admin
from store import models
# Register your models here.


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'brand', 'user', 'created_at')
    fields = ()
    # raw_id_fields = ('user',)
    list_per_page = 10
    search_fields = ['name__icontains', 'brand__icontains']


@admin.register(models.ProductItem)
class ProductItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', "status_show", 'created_at')
    fields = ()
    # raw_id_fields = ('product',)
    list_per_page = 10
    list_editable = ['status_show', 'quantity']
    search_fields = ['product__name__icontains', 'product__brand__icontains']


@admin.register(models.Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'description', 'status_show', 'created_at')
    fields = ()
    # raw_id_fields = ('user', 'product')
    list_per_page = 10
    search_fields = ['product__name__icontains', 'product__brand__icontains', 'desciption__icontains']
    list_editable = ['status_show']


@admin.register(models.Score)
class ScoreAdmin(admin.ModelAdmin):

    list_display = ('product', 'user', 'score', 'created_at')
    fields = ()
    # raw_id_fields = ('user', 'product')
    list_per_page = 10


admin.site.register(models.Cart)
admin.site.register(models.CartItem)
admin.site.register(models.Shop)
