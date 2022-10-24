# Generated by Django 4.1.2 on 2022-10-18 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_product_status_show'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='status_show',
        ),
        migrations.AddField(
            model_name='productitem',
            name='status_show',
            field=models.CharField(choices=[('S', 'SHOW'), ('H', 'HIDDEN'), ('U', 'UNDER REVIEW')], default='H', max_length=1),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
    ]
