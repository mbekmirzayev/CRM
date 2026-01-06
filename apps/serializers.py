from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework.fields import CharField, EmailField, IntegerField
from rest_framework.serializers import ModelSerializer, Serializer

from apps.models import StudentProfile, Course, Group, Category, User
from apps.models.users import Organization


class OrganizationModelSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = 'created_at', 'name', 'is_active'


class CourseModelSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
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


class RegisterSerializer(Serializer):
    email = EmailField(default="bekmirzayevoff@gmail.com")
    first_name = CharField(max_length=50, default="Botir")
    last_name = CharField(max_length=50, default="Botirov")
    password = CharField(write_only=True, default="1")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("Email already registered")
        return value


class VerifyCodeSerializer(Serializer):
    email = EmailField(default="bekmirzayevoff@gmail.com")
    code = IntegerField()


class LoginSerializer(Serializer):
    email = EmailField(default="bekmirzayevoff@gmail.com")
    password = CharField(write_only=True, default="1")

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']

        user = authenticate(email=email, password=password)
        if not user:
            raise ValidationError("Invalid email or password")
        if not user.is_active:
            raise ValidationError("Account is not verified")

        attrs['user'] = user
        return attrs


class LogoutSerializer(Serializer):
    device_id = CharField()
