# Generated by Django 4.1.2 on 2022-10-18 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_alter_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='status_show',
            field=models.CharField(choices=[('S', 'SHOW'), ('H', 'HIDDEN'), ('U', 'UNDER REVIEW')], default='H', max_length=1),
        ),
    ]
