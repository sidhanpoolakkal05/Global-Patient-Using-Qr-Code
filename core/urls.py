from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── REST API ──────────────────────────────────────────────────
    path('api/auth/',         include('accounts.urls')),
    path('api/patients/',     include('patients.urls')),
    path('api/hospitals/',    include('hospitals.urls')),
    path('api/appointments/', include('appointments.urls')),

    # ── Django Template Frontend ──────────────────────────────────
    path('', include('frontend.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,  document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,   document_root=settings.MEDIA_ROOT)
