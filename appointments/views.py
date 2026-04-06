from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Appointment, AppointmentQueue
from .serializers import AppointmentSerializer, AppointmentQueueSerializer
from django.utils import timezone


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Appointment.objects.all().order_by('-appointment_date', '-time_slot')
    filter_backends = [filters.SearchFilter]
    search_fields = ['patient__username', 'doctor__username', 'hospital__name', 'appointment_id']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"DEBUG: Appointment creation failed validation: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for existing active appointment
        patient = request.data.get('patient')
        if patient:
            existing = Appointment.objects.filter(
                patient_id=patient,
                status__in=['pending', 'confirmed', 'checked_in', 'in_progress']
            ).first()
            if existing:
                return Response(
                    {'error': f'Patient already has an active appointment ({existing.status}) at {existing.appointment_date} {existing.time_slot}.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"DEBUG: Appointment creation exception: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        appt = self.get_object()
        user = request.user
        # Only staff roles can delete; patients/doctors should use cancel instead
        if user.role not in ['receptionist', 'hospital_admin', 'admin']:
            return Response(
                {'error': 'Only staff can delete appointments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        # Receptionist can only delete appointments at their hospital
        if user.role == 'receptionist' and appt.hospital != user.hospital:
            return Response(
                {'error': 'You can only delete appointments at your hospital.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.all().order_by('-appointment_date', '-time_slot')
        
        # Date filtering
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(appointment_date=date_param)

        # Patient filtering
        patient_param = self.request.query_params.get('patient')
        if patient_param:
            queryset = queryset.filter(patient_id=patient_param)

        # Status filtering
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        if user.role == 'patient':
            return queryset.filter(patient=user)
        elif user.role == 'doctor':
            return queryset.filter(doctor=user)
        elif user.role in ['receptionist', 'hospital_admin'] and user.hospital:
            return queryset.filter(hospital=user.hospital)
        
        return queryset

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        appt = self.get_object()
        if appt.patient != request.user and request.user.role not in ['admin', 'receptionist', 'hospital_admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        appt.status = 'cancelled'
        appt.cancellation_date = timezone.now()
        appt.cancellation_reason = request.data.get('reason', 'User cancelled')
        appt.save()
        return Response({'status': 'Appointment cancelled'})

    @action(detail=True, methods=['post'], url_path='check-in')
    def check_in(self, request, pk=None):
        appt = self.get_object()
        if request.user.role not in ['receptionist', 'hospital_admin', 'admin']:
            return Response({'error': 'Only staff can perform check-in'}, status=status.HTTP_403_FORBIDDEN)
        
        appt.status = 'checked_in'
        appt.check_in_time = timezone.now()
        appt.save()
        
        # Add to queue
        queue_count = AppointmentQueue.objects.filter(
            doctor=appt.doctor, 
            appointment__appointment_date=timezone.now().date()
        ).count()
        
        AppointmentQueue.objects.get_or_create(
            appointment=appt,
            doctor=appt.doctor,
            defaults={
                'queue_number': queue_count + 1,
                'estimated_wait_time': (queue_count * 15) # Example 15min per patient
            }
        )
        return Response({'status': 'Checked in and added to doctor queue'})

    @action(detail=True, methods=['post'], url_path='pay')
    def pay(self, request, pk=None):
        appt = self.get_object()
        appt.payment_status = 'paid'
        appt.payment_date = timezone.now()
        appt.payment_id = request.data.get('payment_id', 'MANUAL_PAYMENT')
        appt.is_paid = True
        appt.save()
        return Response({'status': 'Payment recorded successfully'})

    @action(detail=False, methods=['get'], url_path='available-slots')
    def available_slots(self, request):
        doctor_id = request.query_params.get('doctor')
        hospital_id = request.query_params.get('hospital')
        date = request.query_params.get('date')
        if not all([doctor_id, hospital_id, date]):
            return Response({'error': 'Provide doctor, hospital, and date parameters'}, status=400)
        
        booked = Appointment.objects.filter(
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            appointment_date=date
        ).exclude(status__in=['cancelled', 'no_show']).count()
        
        return Response({'date': date, 'booked_count': booked})


class AppointmentQueueViewSet(viewsets.ModelViewSet):
    queryset = AppointmentQueue.objects.all()
    serializer_class = AppointmentQueueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = AppointmentQueue.objects.filter(completed_at__isnull=True).order_by('queue_number')
        if user.role == 'doctor':
            return qs.filter(doctor=user)
        elif user.hospital:
            return qs.filter(appointment__hospital=user.hospital)
        return qs

    @action(detail=True, methods=['post'], url_path='call-next')
    def call_next(self, request, pk=None):
        q_entry = self.get_object()
        q_entry.called_at = timezone.now()
        q_entry.appointment.status = 'in_progress'
        q_entry.appointment.save()
        q_entry.save()
        return Response({'status': f'Calling patient {q_entry.queue_number}'})

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        q_entry = self.get_object()
        q_entry.completed_at = timezone.now()
        q_entry.appointment.status = 'completed'
        q_entry.appointment.check_out_time = timezone.now()
        q_entry.appointment.save()
        q_entry.save()
        return Response({'status': f'Completed appointment #{q_entry.queue_number}'})
