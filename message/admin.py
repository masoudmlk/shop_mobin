from django.contrib import admin
from message import models
# Register your models here.

admin.site.register(models.Message)
admin.site.register(models.BadWord)
admin.site.register(models.Group)
