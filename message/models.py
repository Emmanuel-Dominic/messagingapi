import os
import uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from dotenv import load_dotenv

load_dotenv()


# Create your models here.
class ObjectTracking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class ObjectManger(models.Manager):

    def filter_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        return super(ObjectManger, self).filter(content_type=content_type,
                                                object_id=obj_id)


class UserMessage(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True,
                          editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    body = models.TextField(null=True, blank=True)
    body_type = models.CharField(max_length=25, choices=(('TEXT', 'text'), ('VIDEO', 'video'), ('AUDIO', 'audio'),),
                                 blank=False, default='text')
    msg_type = models.CharField(max_length=25, choices=(('DEFAULT', 'default'),
                                                        ('COMMENT', 'comment'),),
                                blank=False, default='default')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={"model__in": ("UserProfile", "Club")},
                                     related_name="sender")
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    objects = ObjectManger()

    def __str__(self):
        return str(self.body)


DEFAULT_AVATAR_URL = os.getenv("DEFAULT_AVATAR_URL")


class UserProfile(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.URLField(max_length=200, blank=True, default=DEFAULT_AVATAR_URL)
    about = models.TextField(max_length=150, blank=True,
                             default='Here I am using the messaging app!')
    is_online = models.BooleanField(default=False, blank=True)
    is_verified = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return str(self.user.username)

    @property
    def messages(self):
        return UserMessage.objects.filter_by_instance(self)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Club(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=50, null=True)
    about = models.TextField(max_length=200, blank=True, default="Let's talk business!")

    # messages = GenericRelation(UserMessage , related_query_name='club')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('owner', 'title',)

    def __str__(self):
        return str(self.title)

    @property
    def messages(self):
        return UserMessage.objects.filter_by_instance(self)

    @property
    def clubusers(self):
        club = ClubUser.objects.filter(club=self.id)
        return UserProfile.objects.filter(id__in=club.values_list('user'))


class ClubUser(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'club',)
