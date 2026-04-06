from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid
import qrcode
from io import BytesIO
from django.core.files import File


class Patient(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    MARITAL_STATUS_CHOICES = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='patient_profile', null=True, blank=True,
    )
    uhid = models.CharField(max_length=20, unique=True, primary_key=True)
    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, default='')

    # Extended personal info
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, default='single')
    occupation = models.CharField(max_length=100, blank=True)

    # Emergency contact
    emergency_contact = models.CharField(max_length=255, blank=True, default='')
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)

    # Medical background
    known_allergies = models.TextField(blank=True, default='')
    chronic_diseases = models.TextField(blank=True, default='')
    current_medications = models.TextField(blank=True)
    past_surgeries = models.TextField(blank=True)
    family_history = models.TextField(blank=True)
    medical_history = models.TextField(blank=True, default='')

    # Lifestyle
    smoking_status = models.BooleanField(default=False)
    alcohol_consumption = models.BooleanField(default=False)
    exercise_frequency = models.CharField(max_length=50, blank=True)

    # Insurance
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)
    insurance_valid_upto = models.DateField(null=True, blank=True)

    # Health metrics
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    bmi = models.FloatField(null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True)

    # Stats
    total_visits = models.IntegerField(default=0)
    last_visit_date = models.DateTimeField(null=True, blank=True)

    qr_code = models.ImageField(upload_to='patient_qrs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.uhid:
            self.uhid = f"GP-{timezone.now().year}-{uuid.uuid4().hex[:6].upper()}"

        # Generate QR code with UHID
        if not self.qr_code:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(self.uhid)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#0F6E56", back_color="white")

            canvas = BytesIO()
            img.save(canvas, format='PNG')
            self.qr_code.save(f'{self.uhid}_qr.png', File(canvas), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.uhid})"


class Consultation(models.Model):
    """A single consultation/treatment record by a doctor for a patient."""
    VISIT_TYPE_CHOICES = [
        ('opd', 'OPD'),
        ('ipd', 'IPD'),
        ('emergency', 'Emergency'),
        ('followup', 'Follow-up'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('referred', 'Referred'),
        ('admitted', 'Admitted'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='consultations_given',
    )
    hospital = models.ForeignKey(
        'hospitals.Hospital', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='consultations',
    )
    consultation_date = models.DateTimeField(auto_now_add=True)
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES, default='opd')

    # Symptoms & Diagnosis
    chief_complaint = models.TextField()
    symptoms = models.TextField(blank=True, default='')
    duration_of_symptoms = models.CharField(max_length=100, blank=True)
    diagnosis = models.CharField(max_length=255)
    differential_diagnosis = models.TextField(blank=True)
    notes = models.TextField(blank=True, default='')
    doctor_notes = models.TextField(blank=True)

    # Vitals
    bp = models.CharField(max_length=20, verbose_name="Blood Pressure", blank=True, default='')
    # Legacy fields still accepted from frontend (blood_pressure, pulse_rate, sp_o2, temperature)
    blood_pressure = models.CharField(max_length=20, blank=True, default='')
    pulse = models.PositiveIntegerField(default=0)
    pulse_rate = models.CharField(max_length=20, blank=True, default='')
    temp = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="Temperature (°F)", default=98.6)
    temperature = models.CharField(max_length=20, blank=True, default='')
    spo2 = models.PositiveIntegerField(verbose_name="Oxygen Saturation (%)", default=98)
    sp_o2 = models.CharField(max_length=20, blank=True, default='')
    respiratory_rate = models.IntegerField(null=True, blank=True)

    # Body metrics
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    bmi = models.FloatField(null=True, blank=True)

    # Examination
    physical_examination = models.TextField(blank=True)
    investigations = models.TextField(blank=True)

    # Treatment & Follow-up
    treatment_plan = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_instructions = models.TextField(blank=True)

    # Status & Referral
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    referred_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='referred_patients'
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.full_name} - Dr.{self.doctor.username} - {self.consultation_date.date()}"


class PatientDocument(models.Model):
    """Medical documents/reports attached to a patient or a specific consultation."""
    DOCUMENT_TYPES = (
        ('prescription', 'Prescription'),
        ('lab_report', 'Lab Report'),
        ('xray', 'X-Ray'),
        ('ct_scan', 'CT Scan'),
        ('mri', 'MRI'),
        ('ultrasound', 'Ultrasound'),
        ('discharge_summary', 'Discharge Summary'),
        ('referral', 'Referral Letter'),
        ('other', 'Other'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents')
    consultation = models.ForeignKey(
        Consultation, on_delete=models.CASCADE,
        related_name='documents', null=True, blank=True
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='patient_documents/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_type} - {self.patient.full_name} ({self.upload_date.date()})"


class Prescription(models.Model):
    FREQUENCY_CHOICES = (
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('thrice_daily', 'Thrice Daily'),
        ('four_times_daily', 'Four Times Daily'),
        ('every_6_hours', 'Every 6 Hours'),
        ('every_8_hours', 'Every 8 Hours'),
        ('every_12_hours', 'Every 12 Hours'),
        ('as_needed', 'As Needed'),
        ('before_meal', 'Before Meal'),
        ('after_meal', 'After Meal'),
        ('bedtime', 'At Bedtime'),
    )

    DURATION_UNIT_CHOICES = (
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    )

    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    # Can link to Medicine (rich) or just store name for quick entry
    medicine = models.ForeignKey(
        'hospitals.Medicine', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='prescriptions'
    )
    medicine_name = models.CharField(max_length=255, help_text="Manual entry if medicine not in master list")
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, blank=True)
    duration_value = models.IntegerField(null=True, blank=True)
    duration_unit = models.CharField(max_length=10, choices=DURATION_UNIT_CHOICES, blank=True)
    duration = models.CharField(max_length=100, blank=True, help_text="Legacy free-text duration")

    instructions = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True)

    is_refillable = models.BooleanField(default=False)
    refill_count = models.IntegerField(default=0)
    refills_used = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    dispensed = models.BooleanField(default=False)
    dispensed_date = models.DateTimeField(null=True, blank=True)

    prescribed_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-populate medicine_name from FK if not provided
        if not self.medicine_name and self.medicine:
            self.medicine_name = self.medicine.name
        super().save(*args, **kwargs)

    def __str__(self):
        name = self.medicine_name or (self.medicine.name if self.medicine else "Unknown")
        return f"{name} for {self.consultation.patient.full_name}"
