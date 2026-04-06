from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, ConsultationViewSet, PrescriptionViewSet, PatientDocumentViewSet

router = DefaultRouter()
router.register(r'consultations', ConsultationViewSet)
router.register(r'prescriptions', PrescriptionViewSet)
router.register(r'documents', PatientDocumentViewSet)
router.register(r'', PatientViewSet, basename='patient')

urlpatterns = [
    path('', include(router.urls)),
]
