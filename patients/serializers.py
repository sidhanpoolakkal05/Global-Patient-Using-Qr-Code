from rest_framework import serializers
from .models import Patient, Consultation, Prescription, PatientDocument


class PrescriptionSerializer(serializers.ModelSerializer):
    medicine_display = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ('prescribed_date',)

    def get_medicine_display(self, obj):
        if obj.medicine:
            return obj.medicine.name
        return obj.medicine_name


class PatientDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = PatientDocument
        fields = '__all__'
        read_only_fields = ('upload_date', 'uploaded_by')

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class ConsultationSerializer(serializers.ModelSerializer):
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    documents = PatientDocumentSerializer(many=True, read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)

    class Meta:
        model = Consultation
        fields = '__all__'
        read_only_fields = ('doctor', 'hospital', 'consultation_date', 'updated_at')

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data['doctor'] = user
        validated_data['hospital'] = getattr(user, 'hospital', None)
        return super().create(validated_data)


class ConsultationSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for nesting inside Patient responses."""
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)

    class Meta:
        model = Consultation
        fields = ('id', 'consultation_date', 'diagnosis', 'chief_complaint', 'doctor_name',
                  'blood_pressure', 'temperature', 'pulse_rate', 'sp_o2', 'respiratory_rate',
                  'weight', 'height', 'bmi', 'visit_type', 'status')


class PatientSerializer(serializers.ModelSerializer):
    consultations = ConsultationSummarySerializer(many=True, read_only=True)
    documents = PatientDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = (
            'uhid', 'user', 'full_name', 'age', 'gender', 'blood_group', 'phone', 
            'email', 'address', 'marital_status', 'occupation', 'emergency_contact', 
            'emergency_contact_phone', 'emergency_contact_relation', 'medical_history',
            'qr_code', 'consultations', 'documents'
        )


class PatientPersonalUpdateSerializer(serializers.ModelSerializer):
    """Restricted fields for patients to edit their own profile."""
    class Meta:
        model = Patient
        fields = (
            'full_name', 'age', 'gender', 'blood_group', 'phone', 'email', 'address',
            'marital_status', 'occupation', 'emergency_contact', 
            'emergency_contact_phone', 'emergency_contact_relation'
        )
