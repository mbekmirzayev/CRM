from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from root.settings import MEDIA_URL, MEDIA_ROOT, STATIC_URL, STATIC_ROOT

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),

    # API
    path('api/v1/', include('apps.urls')),

    path("i18n/", include("django.conf.urls.i18n")),

    # Swagger
) + static(MEDIA_URL, document_root=MEDIA_ROOT) + static(STATIC_URL,
                                                         document_root=STATIC_ROOT)