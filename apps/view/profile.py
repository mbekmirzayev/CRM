#
# @extend_schema(tags=["Profile"])
# class MeView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         return Response(UserModelSerializer(request.user).data)
#
#
# @extend_schema(tags=["session"])
# class MyDevicesView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         devices = Device.objects.filter(
#             user=request.user,
#             is_active=True
#         ).select_related('auth_token')
#
#         data = []
#         for device in devices:
#             is_current = hasattr(device, 'auth_token') and device.auth_token == request.auth
#             data.append({
#                 **DeviceSerializer(device).data,
#                 'is_current': is_current,
#                 'has_token': hasattr(device, 'auth_token')
#             })
#
#         return Response({
#             'total': len(data),
#             'devices': data
#         })
#
#     def delete(self, request, device_id=None):
#         try:
#             device = Device.objects.get(
#                 user=request.user,
#                 device_id=device_id
#             )
#
#             if hasattr(device, 'auth_token'):
#                 device.auth_token.delete()
#
#             device.delete()
#
#             return Response({
#                 'message': 'Qurilma ochirildi'
#             }, status=status.HTTP_200_OK)
#
#         except Device.DoesNotExist:
#             return Response({
#                 'error': 'Qurilma topilmadi'
#             }, status=status.HTTP_404_NOT_FOUND)
#
#
# @extend_schema(tags=[" Profile"])
# class UserProfileViewSet(ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserModelSerializer
#     http_method_names = ['get', 'put']
#     filter_backends = (DjangoFilterBackend,)
#     filter_fields = ['phone']
#
#     def get_object(self):
#         return self.request.user
#
#     # def get_permissions(self):
#     #     if self.action in ['create', 'update', 'partial_update', 'destroy']:
#     #         permission_classes = [IsAdminOrManager]
#     #     else:
#     #         permission_classes = [IsGlobalAdmin]
#     #     return [permission() for permission in permission_classes]

