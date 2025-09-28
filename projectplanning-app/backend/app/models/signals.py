from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .user_profile import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal que crea automáticamente un UserProfile 
    cada vez que se crea un nuevo User
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal que guarda el UserProfile cada vez que se guarda el User
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Si por alguna razón no existe el profile, lo creamos
        UserProfile.objects.create(user=instance)