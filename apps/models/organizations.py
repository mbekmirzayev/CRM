from django.db.models.fields import CharField, BooleanField

from apps.models.base import CreateBaseModel, SlugBaseModel


class Organization(CreateBaseModel, SlugBaseModel):
    name = CharField(max_length=255)
    is_active = BooleanField(default=True)
