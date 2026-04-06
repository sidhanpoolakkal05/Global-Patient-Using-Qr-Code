from rest_framework import serializers
from .models import Appointment, AppointmentQueue


class AppointmentQueueSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='appointment.patient.get_full_name', read_only=True)
    patient_full_name = serializers.CharField(source='appointment.patient.patient_profile.full_name', read_only=True)
    appointment_id = serializers.CharField(source='appointment.appointment_id', read_only=True)
    appointment_status = serializers.CharField(source='appointment.status', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)

    class Meta:
        model = AppointmentQueue
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(source='patient.username', read_only=True)
    patient_full_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    doctor_username = serializers.CharField(source='doctor.username', read_only=True)
    doctor_full_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    slot_time = serializers.SerializerMethodField()
    patient_uhid = serializers.SerializerMethodField()
    queue = AppointmentQueueSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'appointment_id', 'token_number')

    def get_patient_uhid(self, obj):
        if hasattr(obj.patient, 'patient_profile') and obj.patient.patient_profile:
            return obj.patient.patient_profile.uhid
        return "—"

    def get_patient_full_name(self, obj):
        if hasattr(obj.patient, 'patient_profile') and obj.patient.patient_profile:
            return obj.patient.patient_profile.full_name
        return obj.patient.get_full_name() or obj.patient.username

    def get_patient_name(self, obj):
        return self.get_patient_full_name(obj)

    def get_slot_time(self, obj):
        return obj.time_slot.strftime('%H:%M') if obj.time_slot else "—"

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        
        # If no patient is provided, use current user
        if 'patient' not in validated_data and user:
            validated_data['patient'] = user
        
        # Set booked_by to current user
        if user:
            validated_data['booked_by'] = user
            
        # Ensure total_amount is calculated if not provided
        if 'total_amount' not in validated_data or validated_data['total_amount'] == 0:
            fee = validated_data.get('consultation_fee') or validated_data.get('fee') or 0
            discount = validated_data.get('discount', 0)
            validated_data['total_amount'] = fee - discount
            
        return super().create(validated_data)
