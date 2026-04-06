from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, AppointmentQueueViewSet

router = DefaultRouter()
router.register(r'queue', AppointmentQueueViewSet, basename='appointment-queue')
router.register(r'', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]
