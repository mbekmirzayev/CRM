# from django.core.cache import cache
# from drf_spectacular.utils import extend_schema
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView
#
# from apps.models import User, Device, CustomAuthToken
# from apps.serializers import (
#     RegisterSerializer, VerifyCodeSerializer,
#     LoginSerializer, UserModelSerializer, DeviceSerializer
# )
# from apps.utils import normalize_phone, send_verification_code, check_verification_code
#
#
# def get_client_ip(request):
#     """Request'dan IP addressni olish"""
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip
#
#
# @extend_schema(tags=['auth'])
# class RegisterAPI(APIView):
#     serializer_class = RegisterSerializer
#
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         phone = normalize_phone(serializer.validated_data['phone'])
#         user_data = {
#             'phone': phone,
#             'first_name': serializer.validated_data.get('first_name'),
#             'last_name': serializer.validated_data.get('last_name'),
#             'password': serializer.validated_data.get('password'),
#         }
#
#         cache.set(f"temp_user_{phone}", user_data, timeout=300)
#         send_verification_code(phone)
#
#         return Response({
#             "message": "Tasdiqlash kodi yuborildi",
#             "phone": phone
#         }, status=status.HTTP_200_OK)
#
#
# @extend_schema(tags=["auth"])
# class VerifyCodeAPI(APIView):
#     serializer_class = VerifyCodeSerializer
#
#     def post(self, request):
#         serializer = VerifyCodeSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         phone = normalize_phone(serializer.validated_data['phone'])
#         code = serializer.validated_data['code']
#         device_id = serializer.validated_data.get('device_id')
#         device_type = serializer.validated_data.get('device_type', Device.DeviceType.WEB)
#
#         if not check_verification_code(phone, code):
#             return Response({
#                 'error': "Kod notogri yoki muddati o'tgan"
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         user_data = cache.get(f"temp_user_{phone}")
#         if not user_data:
#             return Response({
#                 "error": "Ro'yxatdan o'tish malumotlari topilmadi"
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             user = User.objects.create_user(
#                 phone=phone,
#                 first_name=user_data.get('first_name', ''),
#                 last_name=user_data.get('last_name', ''),
#                 password=user_data.get('password'),
#                 is_active=True
#             )
#         except Exception as e:
#             return Response({
#                 'error': f"Xatolik: {str(e)}"
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         device = None
#         if device_id:
#             device, _ = Device.objects.get_or_create(
#                 user=user,
#                 device_id=device_id,
#                 defaults={
#                     'type': device_type,
#                     'agent': request.META.get('HTTP_USER_AGENT', ''),
#                     'is_active': True
#                 }
#             )
#
#         ip_address = get_client_ip(request)
#         token_instance, token = CustomAuthToken.create_token(
#             user=user,
#             device=device,
#             ip_address=ip_address
#         )
#
#         cache.delete(f"temp_user_{phone}")
#         cache.delete(f"verification_code_{phone}")
#
#         return Response({
#             "message": "Muvaffaqiyatli ro'yxatdan o'tdingiz",
#             'token': token,
#             'expiry': token_instance.expiry,
#             'user': UserModelSerializer(user).data
#         }, status=status.HTTP_201_CREATED)
#
#
# @extend_schema(tags=["auth"])
# class LoginAPI(APIView):
#     serializer_class = LoginSerializer
#
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         user = serializer.validated_data['user']
#         device_id = serializer.validated_data.get('device_id')
#         device_type = serializer.validated_data.get('device_type', Device.DeviceType.WEB)
#
#         device = None
#         if device_id:
#             device, created = Device.objects.update_or_create(
#                 user=user,
#                 device_id=device_id,
#                 defaults={
#                     'type': device_type,
#                     'agent': request.META.get('HTTP_USER_AGENT', ''),
#                     'is_active': True
#                 }
#             )
#
#         ip_address = get_client_ip(request)
#         token_instance, token = CustomAuthToken.create_token(
#             user=user,
#             device=device,
#             ip_address=ip_address
#         )
#
#         return Response({
#             'token': token,
#             'expiry': token_instance.expiry,
#             'user': UserModelSerializer(user).data
#         }, status=status.HTTP_200_OK)
#
#
# @extend_schema(tags=["auth"])
# class LogoutAPI(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         # ✅ Joriy tokenni o'chirish
#         request.auth.delete()
#
#         return Response({
#             'message': 'Muvaffaqiyatli chiqildi'
#         }, status=status.HTTP_200_OK)
#
#
# @extend_schema(tags=["auth"])
# class LogoutAllAPI(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         # ✅ Userning barcha tokenlarini o'chirish
#         deleted_count, _ = CustomAuthToken.objects.filter(user=request.user).delete()
#
#         return Response({
#             'message': f'{deleted_count} ta qurilmadan chiqildi'
#         }, status=status.HTTP_200_OK)
#
#