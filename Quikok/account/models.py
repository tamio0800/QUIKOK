from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver


class user_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    nickname = models.CharField(max_length=40)
    birth_date = models.DateField()
    is_male = models.BooleanField()
    role = models.CharField(max_length=60)
    contact_email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(max_length=60)
    picture_folder = models.CharField(max_length=150)
    tracking_mobile = models.CharField(max_length=130)
    update_someone_by_email = models.CharField(max_length=405)
    update_someone_by_mobile = models.CharField(max_length=65)
    created_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        user_profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()