from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.models import StudentProfile, Course, Group, Category, User
from apps.models.users import Organization
from apps.permissions import IsTeacher, IsGlobalAdmin, IsAdminOrManager
from apps.serializers import TeacherStudentListSerializer, OrganizationModelSerializer, CourseModelSerializer, \
    GroupModelSerializer, CategoryModelSerializer, UserModelSerializer


@extend_schema(tags=["Get me"])
class UserProfileViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer
    http_method_names = ['get', 'put']
    permission_classes = [IsAuthenticated, ]
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['email']

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Organization'])
class OrganizationListAPIView(ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationModelSerializer
    permission_classes = (IsGlobalAdmin,)


@extend_schema(tags=["Course"])
class CourseModelViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CourseModelSerializer
    permission_classes = (IsAdminOrManager,)

    def get_queryset(self):
        user = self.request.user

        if user.is_global_admin:
            return Course.objects.all()

        if user.is_local_admin or user.is_manager:
            return Course.objects.filter(organization=user.organization)

        return Course.objects.none()


@extend_schema(tags=["Group"])
class GroupModelViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = GroupModelSerializer
    permission_classes = (IsAdminOrManager,)

    def get_queryset(self):
        user = self.request.user

        if user.is_global_admin:
            return Group.objects.all()

        if user.is_local_admin or user.is_manager:
            return Group.objects.filter(course__organization=user.organization)

        return Group.objects.none()


@extend_schema(tags=["Category"])
class CategoryModelViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryModelSerializer
    permission_classes = (IsAdminOrManager,)

    def get_queryset(self):
        user = self.request.user

        if user.is_global_admin:
            return Category.objects.all()

        if user.is_local_admin or user.is_manager:
            return Category.objects.filter(organization__courses__category=user.organization.category)

        return Category.objects.none()


@extend_schema(tags=["Teacher's students"])
class TeacherStudentList(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = TeacherStudentListSerializer
    permission_classes = IsAuthenticated, IsTeacher

    def get_queryset(self):
        teacher = self.request.user.teacher_profile

        return StudentProfile.objects.filter(
            enrollments__group__course__teacher=teacher).distinct().prefetch_related(
            'enrollments__group__course')
