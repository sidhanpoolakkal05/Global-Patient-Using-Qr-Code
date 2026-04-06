from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Patient, Consultation, Prescription, PatientDocument
from .serializers import (
    PatientSerializer, PatientPersonalUpdateSerializer, 
    ConsultationSerializer, PrescriptionSerializer, PatientDocumentSerializer
)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'uhid', 'phone']

    def get_serializer_class(self):
        if self.request.user.role == 'patient' and (self.action in ['update', 'partial_update']):
            return PatientPersonalUpdateSerializer
        return PatientSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Patient.objects.all()
        
        # Manual filtering by UHID from query params
        uhid = self.request.query_params.get('uhid')
        if uhid:
            return Patient.objects.filter(uhid=uhid)

        if user.role == 'patient' and hasattr(user, 'patient_profile'):
            return Patient.objects.filter(uhid=user.patient_profile.uhid)
        if user.role in ['receptionist', 'admin', 'hospital_admin', 'doctor']:
            return qs
        return Patient.objects.none()

    def update(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        
        # Security check: patients can only edit their own
        if user.role == 'patient' and instance.user != user:
             return Response({'error': 'You can only edit your own details.'}, status=status.HTTP_403_FORBIDDEN)
             
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        
        # Security check: patients can only edit their own
        if user.role == 'patient' and instance.user != user:
             return Response({'error': 'You can only edit your own details.'}, status=status.HTTP_403_FORBIDDEN)
             
        return super().partial_update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        if user:
            user.delete()

    @action(detail=True, methods=['post'], url_path='treatment')
    def treatment(self, request, pk=None):
        if request.user.role != 'doctor':
            return Response({'error': 'Permission denied. Only doctors can log treatment.'}, status=status.HTTP_403_FORBIDDEN)
        
        patient = self.get_object()
        data = request.data
        
        # Create Consultation
        from .models import Consultation, Prescription
        consultation = Consultation.objects.create(
            patient=patient,
            doctor=request.user,
            hospital=request.user.hospital,
            chief_complaint=data.get('notes', ''),
            diagnosis=data.get('diagnosis', 'Pending Diagnosis'),
            treatment_plan=data.get('notes', ''),
            follow_up_date=data.get('followup_date') or None
        )
        
        # Create multiple prescriptions
        prescribed_medicines = data.get('medicines', [])
        for m_data in prescribed_medicines:
            from hospitals.models import Medicine
            medicine = Medicine.objects.get(id=m_data['id'])
            Prescription.objects.create(
                consultation=consultation,
                medicine=medicine,
                dosage=m_data.get('dosage', ''),
                instructions=m_data.get('dosage', '') # Fallback
            )

        # Complete the appointment — either by explicit ID or by auto-finding the patient's active one
        from appointments.models import Appointment
        appt_id = data.get('appointment_id')
        if appt_id:
            Appointment.objects.filter(id=appt_id).update(
                status='completed',
                check_out_time=timezone.now()
            )
        else:
            # Auto-complete any active appointment for this patient
            active = Appointment.objects.filter(
                patient=patient.user,
                status__in=['pending', 'confirmed', 'checked_in', 'in_progress']
            ).order_by('-appointment_date', '-time_slot').first()
            if active:
                active.status = 'completed'
                active.check_out_time = timezone.now()
                active.save()
            
        return Response({'status': 'Success', 'consultation_id': consultation.id})

    @action(detail=False, methods=['get'], url_path='treatment-history')
    def treatment_history(self, request):
        user = request.user
        patient_id = request.query_params.get('patient_id')
        
        target_patient = None
        if patient_id:
            if user.role not in ['doctor', 'receptionist', 'admin']:
                return Response({'error': 'Unauthorized to view other patient records.'}, status=status.HTTP_403_FORBIDDEN)
            target_patient = Patient.objects.filter(uhid=patient_id).first()
        else:
            if hasattr(user, 'patient_profile'):
                target_patient = user.patient_profile
        
        if not target_patient:
             return Response({'error': 'Patient profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        from .models import Consultation
        qs = Consultation.objects.filter(patient=target_patient).order_by('-consultation_date').prefetch_related('prescriptions__medicine')
        
        # Include patient background in first record or separate header
        bg_data = {
            'allergies': target_patient.known_allergies or 'None',
            'chronic': target_patient.chronic_diseases or 'None',
            'medical_history': target_patient.medical_history or 'None',
            'blood_group': target_patient.blood_group
        }

        data = []
        for c in qs:
            meds = [{
                'name': p.medicine.name if p.medicine else p.medicine_name or '',
                'dosage': p.dosage or p.instructions or '',
                'type': p.medicine.medicine_type if p.medicine else 'D'
            } for p in c.prescriptions.all()]
            
            data.append({
                'id': c.id,
                'date': c.consultation_date.strftime('%Y-%m-%d %H:%M:%S'),
                'display_date': c.consultation_date.strftime('%d %b %Y'),
                'display_time': c.consultation_date.strftime('%I:%M %p'),
                'doctor_name': 'Dr. ' + (c.doctor.get_full_name() or c.doctor.username) if c.doctor else 'Doctor',
                'hospital_name': c.hospital.name if c.hospital else 'MediScan Hospital',
                'notes': c.chief_complaint or '',
                'diagnosis': c.diagnosis or '',
                'vitals': {
                    'bp': c.blood_pressure or '—',
                    'temp': c.temperature or '—',
                    'weight': c.weight or '—',
                },
                'visit_type': c.visit_type or 'General',
                'medicines': meds,
                'follow_up_date': str(c.follow_up_date) if c.follow_up_date else None,
            })
        
        return Response({'history': data, 'background': bg_data})


class ConsultationViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultationSerializer
    queryset = Consultation.objects.all().order_by('-consultation_date')

    def get_queryset(self):
        user = self.request.user
        qs = Consultation.objects.all().order_by('-consultation_date')
        
        # Patients only see their own consultations
        if user.role == 'patient' and hasattr(user, 'patient_profile'):
            qs = qs.filter(patient=user.patient_profile)
        # Doctors see consultations they conducted
        elif user.role == 'doctor':
            qs = qs.filter(doctor=user)
        # Staff see consultations for their hospital
        elif user.hospital:
            qs = qs.filter(hospital=user.hospital)

        patient_uhid = self.request.query_params.get('patient')
        if patient_uhid:
            qs = qs.filter(patient__uhid=patient_uhid)
        return qs


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Prescription.objects.all().order_by('-prescribed_date')
        if user.role == 'patient' and hasattr(user, 'patient_profile'):
            qs = qs.filter(consultation__patient=user.patient_profile)
        elif user.role == 'doctor':
            qs = qs.filter(consultation__doctor=user)
        return qs


class PatientDocumentViewSet(viewsets.ModelViewSet):
    queryset = PatientDocument.objects.all()
    serializer_class = PatientDocumentSerializer

    def get_queryset(self):
        user = self.request.user
        qs = PatientDocument.objects.all().order_by('-upload_date')
        if user.role == 'patient' and hasattr(user, 'patient_profile'):
            qs = qs.filter(patient=user.patient_profile)
        return qs
