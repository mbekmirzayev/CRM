from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField, TextChoices, ForeignKey, CASCADE, OneToOneField
from django.db.models.fields import CharField, BooleanField
from django.utils.translation import gettext_lazy as _

from apps.models.base import CreateBaseModel, SlugBaseModel
from apps.models.base import UUIDBaseModel
from apps.models.managers import UserManager


class Organization(CreateBaseModel, SlugBaseModel):
    name = CharField(max_length=255)
    is_active = BooleanField(default=True)


class User(AbstractUser, UUIDBaseModel):
    class Status(TextChoices):
        GLOBAL_ADMIN = 'global_admin', _('Global admin')
        ADMIN = 'admin', _('Admin')
        MANAGER = 'manager', _('Manager')
        TEACHER = 'teacher', _('Teacher')
        STUDENT = 'student', _('Student')

    organization = ForeignKey('apps.Organization', CASCADE, null=True, blank=True, related_name='users')
    email = EmailField(null=False, blank=False, max_length=255)
    role = CharField(max_length=20, choices=Status.choices, default=Status.STUDENT)
    phone = CharField(max_length=20, blank=True, unique=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    username = None

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_global_admin(self):
        return self.is_superuser

    @property
    def is_local_admin(self):
        return self.role == self.Status.ADMIN and self.is_staff

    @property
    def is_manager(self):
        return self.role == self.Status.MANAGER

    @property
    def is_teacher(self):
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
        FIXED_PLUS_PERCENTAGE = 'fixed_percentage', _('fixed + percentage')

    user = OneToOneField('apps.User', CASCADE, related_name='teacher_profile')
    subject = CharField(max_length=255)
    work_type = CharField(max_length=20, choices=WorkType.choices, default=WorkType.FULL_TIME)
    salary_type = CharField(max_length=55, choices=SalaryType.choices, default=SalaryType.FIXED)
    is_deleted = BooleanField(default=False)

    def delete(self):
        self.is_deleted = True
        self.save()

class StudentProfile(CreateBaseModel):
    class StudentStatus(TextChoices):
        ACTIVE = 'active', _("Active")
        FROZEN = 'frozen', _('Frozen')
        GRADUATED = 'graduated', _('Graduated')
        DROPPED = 'dropped', _('Dropped')

    user = OneToOneField('apps.User', CASCADE, related_name='student_profile')
    parent_phone = CharField(max_length=20)
    status = CharField(max_length=55, choices=StudentStatus.choices)
    is_deleted = BooleanField(default=False)

    def delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.user.get_full_name()}"