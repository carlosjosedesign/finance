from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserPreferences

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Singal: After creating a new user account -> create its user preferences """

    if created:
        UserPreferences.objects.create(user=instance)
        # print("Profile created!")
