from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.models import Enrollment, StudentProfile, Group
from apps.serializers import EnrollmentTransferSerializer


@transaction.atomic
def transfer_student(student, new_group, by_user):
    if Enrollment.objects.filter(student=student, group=new_group, status=Enrollment.Status.ACTIVE).exists():
        return None

    Enrollment.objects.filter(student=student, status=Enrollment.Status.ACTIVE
    ).update(status=Enrollment.Status.DROPPED, left_at=timezone.now().date() )

    new_enrollment = Enrollment.objects.create(
        student=student,
        group=new_group,
        status=Enrollment.Status.ACTIVE,
        created_by=by_user)

    return new_enrollment

@action(detail=False, methods=['post'], url_path='transfer')
def transfer(self, request):
    serializer = EnrollmentTransferSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    student = get_object_or_404(StudentProfile, id=serializer.validated_data['student_id'],
            organization=request.user.organization
    )
    new_group = get_object_or_404(Group, id=serializer.validated_data['group_id'],
        course__organization=request.user.organization
    )

    enrollment = transfer_student(student=student, new_group=new_group, by_user=request.user)
    return Response({"detail": "Student transferred successfully"}, status=status.HTTP_200_OK)
