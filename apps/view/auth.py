from time import timezone

from django.contrib.auth import authenticate, login
from django.core import cache
from django.core.exceptions import ValidationError
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from knox.views import LoginView as KnoxLoginAPIView
from requests import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from apps.models import User, Device, CustomAuthToken
from apps.serializers import RegisterSerializer, VerifyCodeSerializer, \
    LoginSerializer, LogoutSerializer
from apps.utils import check_verification_code, send_verification_code


class RegisterAPIView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        cache.set(f"tmp_password:{email}", password, timeout=10 * 60)
        try:
            send_verification_code(email)
        except ValidationError as e:
            return Response({"message": str(e)}, status=400)

        return Response({"message": "Verification code sent"}, status=status.HTTP_201_CREATED)


# Verify code
class VerifyCodeAPIView(APIView):
    serializer_class = VerifyCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        if not check_verification_code(email, code):
            return Response({"message": "Invalid or expired code"}, status=400)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )

        if created:
            tmp_password = cache.get(f"tmp_password:{email}")
            if not tmp_password:
                return Response({"message": "Password not found. Retry registration"}, status=400)
            user.set_password(tmp_password)
            user.save()
            cache.delete(f"tmp_password:{email}")
        else:
            if not user.is_active:
                user.is_active = True
                user.save()

        return Response({
            "message": "Email verified successfully",
            "email": user.email
        }, status=200)


class CustomLoginAPIView(KnoxLoginAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        if not user:
            return Response({"detail": "Xato ma'lumotlar"}, status=401)

        self._user = user

        # 1. Tozalash: Muddati o'tgan tokenlarni o'chirish (joy bo'shatish uchun)
        CustomAuthToken.objects.filter(user=user, expiry__lt=timezone.now()).delete()

        # 2. Limitni aniqlash (Permissionga qarab)
        if user.is_superuser:
            limit = 10
        elif user.groups.filter(name='Teacher').exists():
            limit = 3
        else:
            limit = 1  # O'quvchilar uchun

        # 3. Limitni tekshirish
        active_devices = Device.objects.filter(user=user, auth_token__isnull=False)

        if active_devices.count() >= limit:
            # Eng eski sessiyani o'chirib yuborish (Avtomatik overwrite)
            oldest_device = active_devices.order_by('created_at').first()
            if oldest_device:
                oldest_device.delete()  # CASCADE bo'lgani uchun token ham o'chadi

        # 4. Qurilmani olish yoki yaratish
        device_id = request.data.get("device_id", "unknown_id")
        device_type = request.data.get("device_type", "web")

        # Bu foydalanuvchi uchun shu qurilmani yaratamiz yoki yangilaymiz
        self.device_obj, _ = Device.objects.update_or_create(
            user=user,
            device_id=device_id,
            defaults={
                "type": device_type,
                "agent": request.META.get("HTTP_USER_AGENT", "")
            }
        )

        login(request, user)
        return super().post(request, *args, **kwargs)

    def get_post_response_data(self, request, token, instance):
        instance.device = self.device_obj
        instance.save(update_fields=["device"])
        return {
            'expiry': self.format_expiry_datetime(instance.expiry),
            "token": token,
            "user": {
                "id": self._user.id,
                "email": self._user.email,
                "first_name": self._user.first_name,
                "last_name": self._user.last_name
            },
            "device": {
                "id": self.device_obj.id,
                "type": self.device_obj.type,
                "agent": self.device_obj.agent
            }
        }


class CustomLogoutView(APIView):
    permission_classes = [IsAuthenticated, ]

    @extend_schema(request=LogoutSerializer)
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device_id = serializer.validated_data["device_id"]

        if hasattr(device_id, 'token') and device_id.token:
            device_id.token.delete()
            device_id.token = None
            device_id.save()

        return Response({"detail": "Logged out successfully"})
