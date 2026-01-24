from django.urls import path
from rest_framework.routers import DefaultRouter

# from apps.view import LoginAPI, LogoutAPI, RegisterAPI, VerifyCodeAPI, UserProfileViewSet
# from apps.view.auth import LogoutAllAPI, MeView, MyDevicesView
from apps.view.views import (
    TeacherStudentList,
    CourseModelViewSet,
    GroupModelViewSet,
    OrganizationModelViewSet,
    CategoryModelViewSet,
)

router = DefaultRouter()
router.register(r'courses', CourseModelViewSet, basename='courses')
router.register(r'categories', CategoryModelViewSet, basename='categories')
router.register(r'groups', GroupModelViewSet, basename='groups')
# router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'organization', OrganizationModelViewSet, basename='organization')

urlpatterns = [
    path('teacher/students', TeacherStudentList.as_view(), name='teacher_students'),
    # path('register', RegisterAPI.as_view(), name='register'),
    # path('verify', VerifyCodeAPI.as_view(), name='verify'),
    # path('login', LoginAPI.as_view(), name='login'),
    # path('logout', LogoutAPI.as_view(), name='logout'),
    # path('logout-all', LogoutAllAPI.as_view(), name='logout-all'),
    # path('me', MeView.as_view(), name='me'),
    # path('devices', MyDevicesView.as_view(), name='devices'),
    # path('devices/<str:device_id>', MyDevicesView.as_view(), name='device-delete'),
]

urlpatterns += router.urls
