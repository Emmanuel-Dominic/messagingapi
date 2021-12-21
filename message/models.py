import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


DEFAULT_AVATAR_URL="https://firebasestorage.googleapis.com/v0/b/messaging-a9715.appspot.com/o/avatars%2Fdefault.png?alt=media&token=6ad7965e-9653-493f-b6c8-364d17594356"
# Create your models here.
class UserProfile(models.Model):
    id = models.UUIDField(default=uuid.uuid4,  unique=True, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.URLField(max_length=200, blank=True, default=DEFAULT_AVATAR_URL)
    about = models.TextField(max_length=150, blank=True, default='Here I am using the messaging app!')
    is_online = models.BooleanField(default=False, blank=True)
    is_verified = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return str(self.user.username)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Club(models.Model):
    id = models.UUIDField(default=uuid.uuid4,  unique=True, primary_key=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=50, null=True)
    about = models.TextField(max_length=200, blank=True, default="Let's talk business!")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('owner', 'title',)

    def __str__(self):
        return str(self.title)


class ClubUser(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'club',)


class UserMessage(models.Model):
    id = models.UUIDField(default=uuid.uuid4,  unique=True, primary_key=True, editable=False)
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="sender")
    reciever_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="sender")
    reciever_id = models.PositiveIntegerField()
    reciever = GenericForeignKey('reciever_type', 'reciever_id')
    body = models.TextField(null=True, blank=True)
    body_type = models.CharField(max_length=25, choices=(('TEXT', 'text'), ('VIDEO', 'video'), ('AUDIO', 'audio'),), blank=False, default='text')
    msg_type = models.CharField(max_length=25, choices=(('DEFAULT', 'default'), ('COMMENT', 'comment'),), blank=False, default='default')
    updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.body)
