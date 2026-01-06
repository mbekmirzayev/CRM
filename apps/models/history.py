from django.db.models import ForeignKey, SET_NULL, OneToOneField, CASCADE
from django.db.models.enums import TextChoices
from django.db.models.fields import DateField, BooleanField, CharField, TextField
from knox.models import AbstractAuthToken

from apps.models.base import CreateBaseModel


class Attendance(CreateBaseModel):
    enrollment = ForeignKey('apps.Enrollment', SET_NULL, null=True, blank=True, related_name='attendances')
    date = DateField()
    present = BooleanField(default=False)


class History(CreateBaseModel):
    class Action(TextChoices):
        STUDENT_JOINED = "STUDENT_JOINED", "Student joined group"
        STUDENT_LEFT = "STUDENT_LEFT", "Student left group"
        GROUP_CREATED = "GROUP_CREATED", "Group created"
        PAYMENT_DONE = "PAYMENT_DONE", "Payment done"
        TEACHER_CHANGED = "TEACHER_CHANGED", "Teacher changed"

    performed_by = ForeignKey('apps.User', SET_NULL, null=True, related_name='actions_performed')
    description = TextField(null=True, blank=True)
    student = ForeignKey('apps.StudentProfile', CASCADE, null=True, blank=True, related_name='student_history')
    group = ForeignKey('apps.Group', SET_NULL, null=True, blank=True, related_name='group_history')
    action = CharField(max_length=255, choices=Action.choices)


class Device(CreateBaseModel):
    class DeviceType(TextChoices):
        WEB = 'web', 'WEB'
        MOBILE = 'mobile', 'MOBILE'

    user = ForeignKey('apps.User', CASCADE, related_name='devices')
    device_id = CharField(max_length=255)
    type = CharField(max_length=20, choices=DeviceType.choices)
    agent = TextField()

    class Meta:
        unique_together = ('user', 'device_id')

    def __str__(self):
        return f"Device({self.device_id} - {self.type})"


class CustomAuthToken(AbstractAuthToken):
    device = OneToOneField('apps.Device', CASCADE, null=True, blank=True, related_name='auth_token')

    def __str__(self):
        return f"AuthToken ({self.user})"
