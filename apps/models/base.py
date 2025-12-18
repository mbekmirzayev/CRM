import uuid

from django.db.models import Func, Model, UUIDField
from django.db.models.fields import DateTimeField, SlugField
from django.utils.text import slugify


class GenRandomUUID(Func):
    function = 'gen_random_uuid'
    template = '%(function)s()'
    output_field = UUIDField()


class UUIDBaseModel(Model):
    id = UUIDField(primary_key=True, db_default=GenRandomUUID(), default=uuid.uuid4(), editable=False)

    class Meta:
        abstract = True


class SlugBaseModel(UUIDBaseModel):
    slug = SlugField(max_length=255, unique=True, db_index=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            if hasattr(self, 'name'):
                base_slug = slugify(self.name)
            elif hasattr(self, 'title'):
                base_slug = slugify(self.title)
            else:
                base_slug = self.id

            self.slug = base_slug
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CreateBaseModel(UUIDBaseModel):
    created_at = DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)
    updated_at = DateTimeField(auto_now=True, blank=True, null=True, editable=False)

    class Meta:
        abstract = True
