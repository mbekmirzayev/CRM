from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField, TextChoices, ForeignKey, CASCADE, OneToOneField
from django.utils.translation import gettext_lazy as _

from apps.models.base import UUIDBaseModel, CreateBaseModel
from apps.models.managers import UserManager


class User(AbstractUser, UUIDBaseModel):
    class Status(TextChoices):
        ADMIN = 'users', _('Admin')
        MANAGER = 'manager', _('Manager')
        TEACHER = 'teacher', _('Teacher')
        STUDENT = 'student', _('Student')

    organization = ForeignKey('apps.organizations', CASCADE, related_name='users')
    email = EmailField(unique=True)
    role = CharField(max_length=20, choices=Status.choices, default=Status.STUDENT)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    username = None

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.Status.ADMIN or self.is_superuser

    @property
    def is_manager(self):
        return self.role == self.Status.MANAGER

    @property
    def is_instructor(self):
        return self.role == self.Status.TEACHER

    @property
    def is_student(self):
        return self.role == self.Status.STUDENT


class TeacherProfile(CreateBaseModel):
    class WorkType(TextChoices):
        FULL_TIME = 'full_time', _('Full_time')
        PART_TIME = 'part_time', _('Part_time')

    class SalaryType(TextChoices):
        FIXED = 'fixed', _('Fixed')
        PERCENTAGE = 'percentage', _('Percentage')
        FIXED_PERCENTAGE = 'fixed_percentage', _('fixed_percentage')

    user = OneToOneField('apps.User', CASCADE, related_name='teacher_profile')
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    phone = CharField(max_length=20, blank=True)
    subject = CharField(max_length=255)
    work_type = CharField(max_length=20, choices=WorkType.choices, default=WorkType.FULL_TIME)
    salary_type = CharField(max_length=55, choices=SalaryType.choices, default=SalaryType.FIXED)


class StudentProfile(CreateBaseModel):
    class StudentStatus(TextChoices):
        ACTIVE = 'active', _("Active")
        FROZEN = 'frozen', _('Frozen')
        GRADUATED = 'graduated', _('Graduated')
        DROPPED = 'dropped', _('Dropped')

    user = OneToOneField('apps.User', CASCADE, related_name='student_profile')
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    phone = CharField(max_length=20, blank=True)
    parent_phone = CharField(max_length=20)
    status = CharField(max_length=55, choices=StudentStatus.choices)
