from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser
from .serializers import (
    RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer, 
    HospitalStaffSerializer, HospitalAdminSerializer
)
from rest_framework import permissions

class IsGlobalAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.role == 'admin' or request.user.is_superuser)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class ProfileView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class UnapprovedUsersView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.role == 'admin' or self.request.user.is_superuser:
            return CustomUser.objects.filter(is_approved=False)
        return CustomUser.objects.none()

class ApproveUserView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        if request.user.role != 'admin' and not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        user.is_approved = True
        user.save()
        return Response({'status': 'Approved', 'user': user.username})

class CreateHospitalStaffView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = HospitalStaffSerializer

    def post(self, request, *args, **kwargs):
        # Only hospital admins can create staff
        if request.user.role != 'hospital_admin':
            return Response({'error': 'Permission denied. Only hospital admins can create staff.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Ensure the hospital admin belongs to a hospital
        if not request.user.hospital:
            return Response({'error': 'Your account is not linked to any hospital.'}, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)

class HospitalStaffListView(generics.ListAPIView):
    serializer_class = HospitalStaffSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role != 'hospital_admin':
            return CustomUser.objects.none()
        
        if not user.hospital:
            return CustomUser.objects.none()
            
        return CustomUser.objects.filter(hospital=user.hospital).exclude(id=user.id)

class UpdateStaffView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = HospitalStaffSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        if request.user.role != 'hospital_admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        staff_user = self.get_object()
        if staff_user.hospital != request.user.hospital:
             return Response({'error': 'Permission denied. Not your hospital staff.'}, status=status.HTTP_403_FORBIDDEN)
             
        return super().update(request, *args, **kwargs)

class DeleteStaffView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        if request.user.role != 'hospital_admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        staff_user = self.get_object()
        if staff_user.hospital != request.user.hospital:
             return Response({'error': 'Permission denied. Not your hospital staff.'}, status=status.HTTP_403_FORBIDDEN)
             
        return super().delete(request, *args, **kwargs)

class CreateHospitalAdminView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = HospitalAdminSerializer

    def post(self, request, *args, **kwargs):
        if request.user.role != 'admin' and not request.user.is_superuser:
            return Response({'error': 'Permission denied. Only global admins can create hospital admins.'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().post(request, *args, **kwargs)

class HospitalAdminsListView(generics.ListAPIView):
    serializer_class = HospitalAdminSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.role != 'admin' and not self.request.user.is_superuser:
            return CustomUser.objects.none()
        hospital_id = self.request.query_params.get('hospital')
        if hospital_id:
            return CustomUser.objects.filter(role='hospital_admin', hospital_id=hospital_id)
        return CustomUser.objects.filter(role='hospital_admin')

class DeleteHospitalAdminView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated, IsGlobalAdmin)

    def delete(self, request, *args, **kwargs):
        user_to_delete = self.get_object()
        if user_to_delete.role != 'hospital_admin':
            return Response({'error': 'Can only delete hospital admins'}, status=status.HTTP_400_BAD_REQUEST)
        return super().delete(request, *args, **kwargs)
class ResetPasswordAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        
        if not username or not email or not new_password:
            return Response({'error': 'Please provide all details.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = CustomUser.objects.get(username=username, email=email)
            user.set_password(new_password)
            user.save()
            return Response({'status': 'Success', 'message': 'Password has been updated.'})
        except CustomUser.DoesNotExist:
            return Response({'error': 'No account found with this username and email.'}, status=status.HTTP_404_NOT_FOUND)
from rest_framework.views import APIView
from django.db.models import Count, Sum
from hospitals.models import Hospital, MedicineMaster,Medicine
from patients.models import Patient
from appointments.models import Appointment

class DashboardStatsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        role = user.role
        stats = {}

        if role == 'admin' or user.is_superuser:
            stats = {
                'total_hospitals': Hospital.objects.count(),
                'pending_hospitals': Hospital.objects.filter(is_verified=False).count(),
                'total_patients': Patient.objects.count(),
                'total_medicines': MedicineMaster.objects.count(),
                'total_users': CustomUser.objects.count()
            }
            print("Admin =================:", stats)  # Debugging statement
        elif role == 'hospital_admin':
            hospital = user.hospital
            today = get_local_today()
            stats = {
                'doctor_count': CustomUser.objects.filter(hospital=hospital, role='doctor').count(),
                'staff_count': CustomUser.objects.filter(hospital=hospital, role='receptionist').count(),
                'total_appointments': Appointment.objects.filter(hospital=hospital).count(),
                'today_appointments': Appointment.objects.filter(hospital=hospital, appointment_date=today).count()
            }
        elif role == 'receptionist':
            hospital = user.hospital
            today = get_local_today()
            stats = {
                'today_appointments': Appointment.objects.filter(hospital=hospital, appointment_date=today).count(),
                'pending_checkins': Appointment.objects.filter(hospital=hospital, status='pending', appointment_date=today).count()
            }
        elif role == 'doctor':
            today = get_local_today()
            stats = {
                'my_appointments_today': Appointment.objects.filter(doctor=user, appointment_date=today).exclude(status='cancelled').count(),
                'patients_treated': Appointment.objects.filter(doctor=user, status='completed').count()
            }
        elif role == 'patient':
            patient_profile = getattr(user, 'patient_profile', None)
            stats = {
                'my_appointments': Appointment.objects.filter(patient=user).count(),
                'last_visit': Appointment.objects.filter(patient=user).order_by('-appointment_date').first().appointment_date if Appointment.objects.filter(patient=user).exists() else None,
                'qr_code_url': patient_profile.qr_code.url if patient_profile and patient_profile.qr_code else None
            }

        return Response(stats)

# Helper for local timezone date
from django.utils import timezone

def get_local_today():
    return timezone.localtime(timezone.now()).date()

