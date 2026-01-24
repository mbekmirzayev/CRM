from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.models import Enrollment, StudentProfile, Group
from apps.serializers import EnrollmentCreateSerializer, EnrollmentDetailSerializer, EnrollmentTransferSerializer
from apps.services import transfer_student


@extend_schema(tags=['enrollment'])
class EnrollmentModelViewSet(ModelViewSet):
    # permission_classes = (IsAuthenticated, IsAdminOrManager,)
    def get_queryset(self):
        user = self.request.user
        return Enrollment.objects.filter(group__course__organization=user.organization)

    def get_serializer_class(self):
        if self.action == 'create':
            return EnrollmentCreateSerializer
        return EnrollmentDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'], url_path='transfer')
    def transfer(self, request):
        serializer = EnrollmentTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student = StudentProfile.objects.get(id=serializer.validated_data['student_id'])
        new_group = Group.objects.get(id=serializer.validated_data['group_id'])

        enrollment = transfer_student(student=student, new_group=new_group, by_user=request.user)

        return Response(
            {"detail": "Student transferred successfully"},
            status=status.HTTP_200_OK
        )
