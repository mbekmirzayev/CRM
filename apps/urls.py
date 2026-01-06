from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.view import CustomLoginAPIView, CustomLogoutView, RegisterAPIView, VerifyCodeAPIView
from apps.view.views import (
    TeacherStudentList,
    CourseModelViewSet,
    GroupModelViewSet,
    OrganizationListAPIView,
    CategoryModelViewSet,
)

router = DefaultRouter()
router.register(r'courses', CourseModelViewSet, basename='courses')
router.register(r'categories', CategoryModelViewSet, basename='categories')
router.register(r'groups', GroupModelViewSet, basename='groups')

urlpatterns = [
    path('teacher/students', TeacherStudentList.as_view(), name='teacher_students'),
    path('organizations-list', OrganizationListAPIView.as_view(), name='organization_list'),
    path('auth/register', RegisterAPIView.as_view(), name='send_code'),
    path('auth/verify_code', VerifyCodeAPIView.as_view(), name='verify_code'),
    path('login', CustomLoginAPIView.as_view(), name='knox_login'),
    path('logout', CustomLogoutView.as_view(), name='knox_logout'),

]

urlpatterns += router.urls
