import uuid
from django.db import models


class TimeStampedModel(models.Model):
    created = models.DateTimeField(db_index=True, auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Extensions(models.Model):
    """ Best practice for lookup field url instead pk or slug """

    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Best practice for lookup field url instead pk or slug.
    for security
    """

    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
