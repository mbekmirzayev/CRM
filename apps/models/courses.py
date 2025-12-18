from django.db.models import ManyToManyField, ForeignKey, CASCADE, TextChoices
from django.db.models.fields import CharField, DecimalField, IntegerField, TimeField
from django.utils.translation import gettext_lazy as _

from apps.models.base import CreateBaseModel, UUIDBaseModel, SlugBaseModel


class Category(UUIDBaseModel, SlugBaseModel):
    name = CharField(max_length=255)


class Course(CreateBaseModel, SlugBaseModel):
    category = ForeignKey('apps.Category', CASCADE, related_name='courses')
    title = CharField(max_length=255, verbose_name=_("Course title"))
    teacher = ManyToManyField('apps.TeacherProfile',  related_name='courses')
    duration = CharField(max_length=255, verbose_name='Duration')
    lesson_count = IntegerField(default=0)
    price = DecimalField(max_digits=10, decimal_places=2)

    @property
    def teacher_images(self):
        return [i.image.url for i in self.teacher.all() if i.image]

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    def __str__(self):
        return self.title


class Group(CreateBaseModel):
    class GroupStatus(TextChoices):
        ACTIVE = 'active', _('Active')
        CLOSED = 'closed', _('Closed')

    course = ForeignKey('apps.Course', CASCADE, related_name='groups')
    status = CharField(max_length=55, choices=GroupStatus.choices)
    start_time = TimeField()
    end_time = TimeField()


class GroupSchedule(UUIDBaseModel):
    class DAYS(TextChoices):
        MONDAY = 'mon', _('Monday')
        TUESDAY = 'tue', _('Tuesday')
        WEDNESDAY = 'wed', _('Wednesday')
        THURSDAY = 'thu', _('Thursday')
        FRIDAY = 'fri', _('Friday')
        SATURDAY = 'sat', _('Saturday')
        SUNDAY = 'sun', _('Sunday')

    group = ForeignKey('apps.Group', CASCADE, related_name='schedule_days')
    days = CharField(max_length=10, choices=DAYS.choices)


class Enrollment(CreateBaseModel):
    student = ForeignKey('apps.StudentProfile', CASCADE, related_name='enrollments')
    group = ForeignKey('apps.Group', CASCADE)
