from django.db.models import ForeignKey, CASCADE, TextChoices, SET_NULL
from django.db.models.fields import DecimalField, CharField
from django.utils.translation import gettext_lazy as _

from apps.models.base import CreateBaseModel


class Payment(CreateBaseModel):
    class Status(TextChoices):
        PAID = 'paid', _('Paid')
        UNPAID = 'unpaid', _('Unpaid')
        PARTIAL = 'partial', _('Partial')
        OVERDUE = 'overdue', _('Overdue')

    student = ForeignKey('apps.StudentProfile', SET_NULL, null=True, blank=True, related_name='student_payments')
    course = ForeignKey('apps.Course', SET_NULL, null=True, blank=True, related_name='course_payments')
    group = ForeignKey('apps.Group', SET_NULL, null=True, blank=True, related_name='group_payments')
    amount = DecimalField(max_digits=10, decimal_places=2)
    status = CharField(max_length=55, choices=Status.choices, default=Status.UNPAID)
