import time
from django.urls import reverse
from django.db import models
from shop import settings


class Group(models.Model):
    name = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, 'members', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def app_url(self):
        return reverse('group_page', kwargs={"pk": self.pk})


class Message(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    related_group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def last_message(group_name):
        return Message.objects.filter(related_group__name=group_name).order_by("-created_at")

    def __str__(self):
        return str(self.author)


class BadWord(models.Model):
    content = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

