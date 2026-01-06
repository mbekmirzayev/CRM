from apps.models.base import UUIDBaseModel, CreateBaseModel, SlugBaseModel
from apps.models.courses import Course, Category, Enrollment, Group, GroupSchedule
from apps.models.history import Attendance, History, Device, CustomAuthToken
from apps.models.payments import Payment
from apps.models.users import User, StudentProfile, TeacherProfile



__all__ = [
    'Course', 'Category', 'Enrollment', 'Group', 'GroupSchedule', 'Attendance', 'Device', 'CustomAuthToken', 'History', 'Payment', 'User', 'SlugBaseModel', 'UUIDBaseModel', 'CreateBaseModel', 'StudentProfile', 'TeacherProfile'
]