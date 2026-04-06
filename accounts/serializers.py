from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomUser
from patients.models import Patient
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class UserSerializer(serializers.ModelSerializer):
    hospital_name = serializers.SerializerMethodField()
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'role', 'is_approved', 'hospital', 'hospital_name')
        read_only_fields = ('is_approved',)

    def get_hospital_name(self, obj):
        return obj.hospital.name if obj.hospital else None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.role == 'patient' and hasattr(instance, 'patient_profile'):
            pp = instance.patient_profile
            ret['uhid'] = pp.uhid
            ret['medical_history'] = pp.medical_history
            ret['blood_group'] = pp.blood_group
            ret['age'] = pp.age
            ret['gender'] = pp.gender
            ret['phone'] = pp.phone
        return ret

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    # Patient specific fields
    full_name = serializers.CharField(required=False, write_only=True)
    phone = serializers.CharField(required=False, write_only=True)
    age = serializers.IntegerField(required=False, write_only=True)
    gender = serializers.CharField(required=False, write_only=True)
    blood_group = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'role', 'full_name', 'phone', 'age', 'gender', 'blood_group', 'hospital')

    def validate_role(self, value):
        if value != 'patient':
            raise serializers.ValidationError("Only patients can self-register. Other roles must be added by a hospital administrator.")
        return value

    def create(self, validated_data):
        role = 'patient' # Force role to patient
        hospital = validated_data.get('hospital', None)
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=role,
            hospital=hospital
        )

        if role == 'patient':
            # Patient profile is created by signals or manually here. 
            # In our current setup, we do it here.
            # UHID is generated in Patient.save, but we can ensure it's saved.
            patient = Patient.objects.create(
                user=user,
                full_name=validated_data.get('full_name', ''),
                phone=validated_data.get('phone', ''),
                email=validated_data.get('email', ''),
                age=validated_data.get('age', 0),
                gender=validated_data.get('gender', 'Male'),
                blood_group=validated_data.get('blood_group', 'O+'),
            )

            # Send Email Notification with QR Code
            if user.email:
                try:
                    subject = f"🏥 MediScan Health ID - {patient.full_name} ({patient.uhid})"
                    
                    # HTML Content for better deliverability
                    html_content = f"""
                    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                        <h2 style="color: #064E3B; text-align: center;">Welcome to MediScan</h2>
                        <p>Hello <strong>{patient.full_name}</strong>,</p>
                        <p>Your digital health account has been created successfully. Below is your unique identifier for all clinical visits:</p>
                        
                        <div style="background: #f0fdf4; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; border: 1px solid #dcfce7;">
                            <span style="font-size: 12px; color: #166534; text-transform: uppercase; letter-spacing: 1px;">Universal Health ID</span><br/>
                            <strong style="font-size: 24px; color: #064E3B; letter-spacing: 2px;">{patient.uhid}</strong>
                        </div>
                        
                        <p><strong>Next Steps:</strong></p>
                        <ul>
                            <li>We have attached your <strong>Digital QR Health Card</strong> to this email.</li>
                            <li>Please present this QR code at any affiliated hospital front desk for instant check-in.</li>
                            <li>Your medical history and prescriptions will be safely linked to this ID.</li>
                        </ul>
                        
                        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
                        <p style="font-size: 12px; color: #666; text-align: center;">
                            This is an automated message from MediScan HMS. Please do not reply to this email.
                        </p>
                    </div>
                    """
                    
                    text_content = strip_tags(html_content)
                    
                    email_msg = EmailMultiAlternatives(
                        subject,
                        text_content,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                    )
                    email_msg.attach_alternative(html_content, "text/html")
                    
                    if patient.qr_code:
                        email_msg.attach_file(patient.qr_code.path)
                    
                    email_msg.send()
                except Exception as e:
                    print(f"Failed to send email: {e}")

        return user

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if hasattr(instance, 'patient_profile') and instance.patient_profile:
            ret['uhid'] = instance.patient_profile.uhid
        return ret

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_approved:
            raise AuthenticationFailed('Your account is pending approval by an administrator.')
        
        data['role'] = self.user.role
        data['username'] = self.user.username
        if self.user.hospital:
            data['hospital_name'] = self.user.hospital.name
        if self.user.role == 'patient' and hasattr(self.user, 'patient_profile'):
            data['uhid'] = self.user.patient_profile.uhid
        return data

from hospitals.models import Hospital, DoctorProfile, StaffProfile

class HospitalStaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    # Custom fields for profiles
    specialization = serializers.CharField(required=False, allow_blank=True, write_only=True)
    qualification = serializers.CharField(required=False, allow_blank=True, write_only=True)
    experience_years = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    registration_number = serializers.CharField(required=False, allow_blank=True, write_only=True)
    consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True, write_only=True)
    bio = serializers.CharField(required=False, allow_blank=True, write_only=True)
    department = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'role', 'is_approved', 'hospital',
                  'specialization', 'qualification', 'experience_years', 'registration_number', 
                  'consultation_fee', 'bio', 'department')
        read_only_fields = ('is_approved', 'hospital')

    def create(self, validated_data):
        hospital = self.context['request'].user.hospital
        role = validated_data.get('role')
        
        # Pop profile data with defaults
        spec = validated_data.pop('specialization', '') or ''
        qual = validated_data.pop('qualification', '') or ''
        exp = validated_data.pop('experience_years', 0) or 0
        reg = validated_data.pop('registration_number', '') or ''
        fee = validated_data.pop('consultation_fee', 0) or 0
        bio = validated_data.pop('bio', '') or ''
        dept = validated_data.pop('department', '') or ''

        if role not in ['doctor', 'receptionist']:
            raise serializers.ValidationError("Only doctors and receptionists can be created.")

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=role,
            hospital=hospital,
            is_approved=True,
            phone=validated_data.get('phone', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        if role == 'doctor':
             DoctorProfile.objects.create(
                 user=user,
                 specialization=spec or 'other',
                 qualification=qual,
                 experience_years=exp,
                 registration_number=reg,
                 consultation_fee=fee,
                 bio=bio
             )
        elif role == 'receptionist':
            StaffProfile.objects.create(
                user=user,
                department=dept or 'Reception',
                qualification=qual
            )

        return user

    def update(self, instance, validated_data):
        # Handle profile fields with defaults
        spec = validated_data.pop('specialization', None)
        qual = validated_data.pop('qualification', None)
        exp = validated_data.pop('experience_years', None)
        reg = validated_data.pop('registration_number', None)
        fee = validated_data.pop('consultation_fee', None)
        bio = validated_data.pop('bio', None)
        dept = validated_data.pop('department', None)

        # Update user instance
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()

        # Update profiles
        if instance.role == 'doctor':
            profile, _ = DoctorProfile.objects.get_or_create(user=instance)
            if spec is not None: profile.specialization = spec or 'other'
            if qual is not None: profile.qualification = qual
            if exp is not None: profile.experience_years = exp or 0
            if reg is not None: profile.registration_number = reg
            if fee is not None: profile.consultation_fee = fee or 0
            if bio is not None: profile.bio = bio
            profile.save()
        elif instance.role == 'receptionist':
            profile, _ = StaffProfile.objects.get_or_create(user=instance)
            if dept is not None: profile.department = dept or 'Reception'
            if qual is not None: profile.qualification = qual
            profile.save()

        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.role == 'doctor' and hasattr(instance, 'doctor_profile'):
            ret['specialization'] = instance.doctor_profile.specialization
            ret['qualification'] = instance.doctor_profile.qualification
            ret['experience_years'] = instance.doctor_profile.experience_years
            ret['registration_number'] = instance.doctor_profile.registration_number
            ret['consultation_fee'] = instance.doctor_profile.consultation_fee
        elif instance.role == 'receptionist' and hasattr(instance, 'staff_profile'):
            ret['department'] = instance.staff_profile.department
            ret['qualification'] = instance.staff_profile.qualification
        return ret
class HospitalAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'full_name', 'email', 'role', 'hospital')
        extra_kwargs = {
            'role': {'read_only': True},
            'hospital': {'required': True}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role='hospital_admin',
            hospital=validated_data['hospital'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.is_approved = True
        user.save()
        return user

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['hospital_name'] = instance.hospital.name if instance.hospital else ""
        return ret
