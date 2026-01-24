from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from rest_framework.fields import CharField, IntegerField, ChoiceField, UUIDField, DateTimeField, SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer

from apps.models import StudentProfile, Course, Group, Category, Enrollment, Payment, Attendance
from apps.models import User, Device
from apps.models.users import Organization
from apps.utils import normalize_phone


class EnrollmentCreateSerializer(ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ('student', 'group')

    def validate(self, attrs):
        student = attrs['student']
        group = attrs['group']

        if Enrollment.objects.filter(student=student, course=group.course, status='active').exists():
            raise ValidationError(
                "Student already has an active group for this course."
            )

        return attrs

class EnrollmentTransferSerializer(Serializer):
    student_id = UUIDField()
    group_id = UUIDField()


class PaymentSerializer(ModelSerializer):

    status = CharField(read_only=True)
    paid_at  = DateTimeField(read_only=True)
    remaining_amount = SerializerMethodField()
    class Meta:
        model = Payment
        fields = '__all__'

    def get_remaining_amount(self, obj):
        return obj.total_amount - obj.paid_amount

class EnrollmentDetailSerializer(ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'


class AttendanceSerializer(ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'


class OrganizationModelSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = 'created_at', 'name', 'is_active'


class CourseModelSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class CategoryModelSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class GroupModelSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = 'id', 'course', 'name', 'status', 'start_time', 'end_time'


class TeacherStudentListSerializer(ModelSerializer):
    first_name = CharField(source='user.phone', read_only=True)
    last_name = CharField(source='user.phone', read_only=True)
    phone = CharField(source='user.phone', read_only=True)

    class Meta:
        model = StudentProfile
        fields = 'id', 'first_name', 'last_name', 'phone'


class DeviceSerializer(ModelSerializer):
    class Meta:
        model = Device
        fields = ('id', 'device_id', 'type', 'agent', 'last_active', 'is_active')
        read_only_fields = ('id', 'last_active', 'is_active')


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'first_name', 'last_name', 'is_active')


class RegisterSerializer(Serializer):
    phone = CharField(default="+998931970019")
    first_name = CharField(max_length=50, default="Botir")
    last_name = CharField(max_length=50, default="Qodirov")
    password = CharField(write_only=True, min_length=6, default="salom19")

    def validate_phone(self, value):
        value = normalize_phone(value)
        if User.objects.filter(phone=value).exists():
            raise ValidationError("Bu telefon raqami allaqachon ro'yxatdan o'tgan")
        return value


class VerifyCodeSerializer(Serializer):
    phone = CharField(default="+998931970019")
    code = IntegerField()
    device_id = CharField(required=False, allow_blank=True)
    device_type = ChoiceField(choices=Device.DeviceType.choices, default=Device.DeviceType.WEB)


class LoginSerializer(Serializer):
    phone = CharField(default="+998931970019")
    password = CharField(write_only=True, default="salom19")
    device_id = CharField(required=False, allow_blank=True)
    device_type = ChoiceField(choices=Device.DeviceType.choices, default=Device.DeviceType.WEB)

    def validate(self, attrs):
        phone = normalize_phone(attrs.get('phone'))
        password = attrs.get('password')

        try:
            user = User.objects.only(
                'id', 'phone', 'password', 'first_name',
                'last_name', 'is_active'
            ).get(phone=phone)
        except User.DoesNotExist:
            raise ValidationError("Telefon raqam yoki parol noto'g'ri")

        if not user.is_active:
            raise ValidationError("Akkaunt faol emas")

        if not check_password(password, user.password):
            raise ValidationError("Telefon raqam yoki parol noto'g'ri")

        attrs['user'] = user
        return attrs
