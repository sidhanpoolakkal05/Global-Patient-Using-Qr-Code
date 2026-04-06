from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, ProfileView, UnapprovedUsersView, ApproveUserView, 
    CustomTokenObtainPairView, CreateHospitalStaffView, DashboardStatsView,
    HospitalAdminsListView, CreateHospitalAdminView, HospitalStaffListView,
    DeleteHospitalAdminView, UpdateStaffView, DeleteStaffView, ResetPasswordAPIView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='auth_profile'),
    path('unapproved/', UnapprovedUsersView.as_view(), name='unapproved_users'),
    path('approve/<int:pk>/', ApproveUserView.as_view(), name='approve_user'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('hospital-admins/', HospitalAdminsListView.as_view(), name='hospital_admins_list'),
    path('create-hospital-admin/', CreateHospitalAdminView.as_view(), name='create_hospital_admin'),
    path('hospital-admins/<int:pk>/', DeleteHospitalAdminView.as_view(), name='delete_hospital_admin'),
    path('create-staff/', CreateHospitalStaffView.as_view(), name='create_staff'),
    path('staff/', HospitalStaffListView.as_view(), name='hospital_staff_list'),
    path('staff/<int:pk>/', UpdateStaffView.as_view(), name='update_staff'),
    path('staff/delete/<int:pk>/', DeleteStaffView.as_view(), name='delete_staff'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset_password'),
]
