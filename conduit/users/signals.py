from django.contrib.auth.models import AbstractBaseUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User


@receiver(post_save, sender=User)
def save_tag(sender: AbstractBaseUser, instance: User, created: bool, **kwargs):

    if created and not instance.tag:
        instance.generate_tag()