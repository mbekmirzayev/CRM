from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.models import Payment
from apps.permissions import IsAdminOrManager
from apps.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrManager,)
    queryset = Payment.objects.all().order_by('-created_at')
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'student', 'course', 'group']
    search_fields = ['student__first_name', 'student__last_name', 'course__title']
