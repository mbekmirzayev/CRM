# root/urls.py
from django.conf.global_settings import STATIC_ROOT
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from root.settings import MEDIA_ROOT, MEDIA_URL, STATIC_URL

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),

    # API
    path('api/v1/', include('apps.urls')),

    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path("i18n/", include("django.conf.urls.i18n")),

    # Swagger
    path('api/schema', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
) + static(MEDIA_URL, document_root=MEDIA_ROOT) + static(STATIC_URL,
                                                         document_root=STATIC_ROOT)
