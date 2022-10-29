from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from message.models import Group


@receiver(post_save, sender=Group)
def add_creator_to_group(sender, **kwargs):
    if kwargs['created']:
        group_object = kwargs['instance']
        if isinstance(group_object, Group):
            group_object.members.add(group_object.creator)
           