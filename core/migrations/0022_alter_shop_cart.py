# Generated by Django 4.1.2 on 2022-10-18 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_remove_product_status_show_productitem_status_show_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.cart', unique=True),
        ),
    ]