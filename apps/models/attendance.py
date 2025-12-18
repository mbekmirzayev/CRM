from django.db.models import CASCADE, ForeignKey
from django.db.models.fields import DateField, BooleanField

from apps.models.base import CreateBaseModel


class Attendance(CreateBaseModel):
    enrollment = ForeignKey('apps.Enrollment', CASCADE, related_name='attendances')
    date = DateField()
    present = BooleanField(default=False)
