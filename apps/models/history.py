from django.db import models
from django.db.models import CASCADE, ForeignKey, OneToOneField, CharField, TextField, TextChoices
from django.db.models import SET_NULL
from django.db.models.fields import DateField, BooleanField
from django.utils import timezone
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
        WEB = 'web', 'Web Browser'
        MOBILE = 'mobile', 'Mobile App'
        DESKTOP = 'desktop', 'Desktop App'
        TABLET = 'tablet', 'Tablet'

    user = ForeignKey('apps.User', CASCADE, related_name='devices')
    device_id = CharField(max_length=255, db_index=True)
    type = CharField(max_length=20, choices=DeviceType.choices, default=DeviceType.WEB)
    agent = TextField(blank=True, default='')
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'device_id')
        ordering = ['-last_active']
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'

    def __str__(self):
        return f"{self.user.phone} - {self.type} ({self.device_id[:8]}...)"

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active'])


class CustomAuthToken(AbstractAuthToken):

    device = OneToOneField('apps.Device', CASCADE, null=True, blank=True, related_name='auth_token')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Auth Token'
        verbose_name_plural = 'Auth Tokens'
        ordering = ['-created']

    def __str__(self):
        device_info = f" - {self.device.type}" if self.device else ""
        return f"Token: {self.user.phone}{device_info}"

    @classmethod
    def create_token(cls, user, device=None, ip_address=None):

        if device:
            cls.objects.filter(device=device).delete()
        else:
            cls.objects.filter(user=user, device__isnull=True).delete()

        user_tokens_count = cls.objects.filter(user=user).count()
        if user_tokens_count >= 10:
            oldest_token = cls.objects.filter(user=user).order_by('created').first()
            if oldest_token:
                oldest_token.delete()

        instance, token = cls.objects.create(user=user)
        instance.device = device
        instance.ip_address = ip_address
        instance.save(update_fields=['device', 'ip_address'])

        if device:
            device.last_active = timezone.now()
            device.save(update_fields=['last_active'])

        return instance, token

    def delete(self, *args, **kwargs):
        if self.device:
            self.device.deactivate()
        super().delete(*args, **kwargs)
