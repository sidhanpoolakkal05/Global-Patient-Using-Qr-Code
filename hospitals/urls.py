from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HospitalViewSet, HospitalSettingsView, DoctorSlotViewSet, 
    MedicineViewSet, MedicineStockViewSet, DoctorScheduleViewSet, DoctorLeaveViewSet
)

router = DefaultRouter()
router.register(r'doctor-slots', DoctorSlotViewSet, basename='doctorslot')
router.register(r'doctor-schedules', DoctorScheduleViewSet, basename='doctorschedule')
router.register(r'doctor-leaves', DoctorLeaveViewSet, basename='doctorleave')
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'medicine-stocks', MedicineStockViewSet, basename='medicinestock')
router.register(r'', HospitalViewSet, basename='hospital')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:hospital_pk>/settings/', HospitalSettingsView.as_view(), name='hospital-settings'),
]
