from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver

# from conduit.storage.models import Drive
from .models import User

# from conduit.storage.choices import DriveType


@receiver(post_save, sender=User)
def save_tag_and_prep_drive(
    sender: AbstractBaseUser, instance: User, created: bool, **kwargs
):

    if created:
        if not instance.tag:
            instance.generate_tag()

        instance.prep_personal_drive()
