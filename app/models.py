from uuid6 import uuid7
from django.db import models
from django.db.models import QuerySet

# Create your models here.

ACTIVE = "ACTIVE"
DELETED = "DELETED"

class NonDeletedObjectsManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().exclude(status="DELETED").order_by("-created_at")
    
class Profile(models.Model):
    STATUS_CHOICES = (
        (ACTIVE, ACTIVE),
        (DELETED, DELETED)
    )
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False, unique=True)
    name = models.CharField(max_length=256)
    gender = models.CharField(max_length=10)
    gender_probability = models.FloatField(default=0)
    sample_size = models.PositiveIntegerField(default=0)
    age = models.PositiveSmallIntegerField(default=0)
    age_group = models.CharField(max_length=10)
    country_id = models.CharField(max_length=4)
    country_probability = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, default=ACTIVE)

    all_objects = models.Manager()
    objects = NonDeletedObjectsManager()