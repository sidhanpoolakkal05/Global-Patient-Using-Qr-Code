from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'System Administrator'),
        ('hospital', 'Hospital Administrator'),
        ('doctor', 'Doctor'),
        ('staff', 'Hospital Staff'),
        ('patient', 'Patient'),
    )
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='patient')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
        
    def __str__(self):
        return f"{self.get_full_name()} - {self.get_user_type_display()}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def generate_qr_code(self, data=None):
        """Generate QR code for the user"""
        if not data:
            data = f"USER_ID:{self.id}\nNAME:{self.get_full_name()}\nTYPE:{self.user_type}\nEMAIL:{self.email}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')
        
        # Resize image
        img = img.resize((300, 300))
        
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        
        filename = f'qr_codes/user_{self.id}_{timezone.now().timestamp()}.png'
        self.qr_code.save(filename, File(buffer), save=False)
        self.save()
        
        return self.qr_code
    
    def get_user_profile(self):
        """Get the specific profile based on user type"""
        if self.user_type == 'hospital' and hasattr(self, 'hospital_profile'):
            return self.hospital_profile
        elif self.user_type == 'doctor' and hasattr(self, 'doctor_profile'):
            return self.doctor_profile
        elif self.user_type == 'staff' and hasattr(self, 'employee_profile'):
            return self.employee_profile
        elif self.user_type == 'patient' and hasattr(self, 'patient_profile'):
            return self.patient_profile
        return None

class Hospital(models.Model):
    HOSPITAL_TYPE_CHOICES = (
        ('general', 'General Hospital'),
        ('specialty', 'Specialty Hospital'),
        ('teaching', 'Teaching Hospital'),
        ('clinic', 'Clinic'),
        ('research', 'Research Hospital'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile')
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100, unique=True)
    hospital_type = models.CharField(max_length=20, choices=HOSPITAL_TYPE_CHOICES, default='general')
    description = models.TextField(blank=True)
    
    # Contact Information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Hospital Details
    established_year = models.IntegerField(null=True, blank=True)
    bed_count = models.IntegerField(default=0)
    ambulance_count = models.IntegerField(default=0)
    emergency_available = models.BooleanField(default=True)
    icu_available = models.BooleanField(default=True)
    pharmacy_available = models.BooleanField(default=True)
    lab_facilities = models.BooleanField(default=True)
    
    # Images
    logo = models.ImageField(upload_to='hospital_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='hospital_covers/', blank=True, null=True)
    
    # Status
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Doctor(models.Model):
    SPECIALIZATION_CHOICES = (
        ('cardiology', 'Cardiology'),
        ('dermatology', 'Dermatology'),
        ('neurology', 'Neurology'),
        ('pediatrics', 'Pediatrics'),
        ('orthopedics', 'Orthopedics'),
        ('gynecology', 'Gynecology'),
        ('ophthalmology', 'Ophthalmology'),
        ('ent', 'ENT Specialist'),
        ('psychiatry', 'Psychiatry'),
        ('dentistry', 'Dentistry'),
        ('radiology', 'Radiology'),
        ('surgery', 'General Surgery'),
        ('internal_medicine', 'Internal Medicine'),
        ('emergency', 'Emergency Medicine'),
        ('other', 'Other'),
    )
    
    QUALIFICATION_CHOICES = (
        ('mbbs', 'MBBS'),
        ('md', 'MD'),
        ('ms', 'MS'),
        ('dm', 'DM'),
        ('mch', 'MCh'),
        ('bds', 'BDS'),
        ('other', 'Other'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors')
    
    # Professional Details
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    sub_specialization = models.CharField(max_length=200, blank=True)
    qualification = models.CharField(max_length=50, choices=QUALIFICATION_CHOICES)
    other_qualification = models.CharField(max_length=500, blank=True)
    experience_years = models.IntegerField(default=0)
    registration_number = models.CharField(max_length=100, unique=True)
    registration_council = models.CharField(max_length=200)
    
    # Consultation Details
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    follow_up_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_seats = models.IntegerField(default=10)
    consultation_duration = models.IntegerField(default=15, help_text="Minutes per consultation")
    
    # Availability
    is_available = models.BooleanField(default=True)
    is_on_leave = models.BooleanField(default=False)
    leave_start_date = models.DateField(null=True, blank=True)
    leave_end_date = models.DateField(null=True, blank=True)
    
    # Ratings
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_patients = models.IntegerField(default=0)
    total_reviews = models.IntegerField(default=0)
    
    # Biography
    bio = models.TextField(blank=True)
    languages = models.CharField(max_length=200, help_text="Comma-separated languages", default="English")
    
    # Media
    profile_picture = models.ImageField(upload_to='doctor_profiles/', blank=True, null=True)
    signature = models.ImageField(upload_to='doctor_signatures/', blank=True, null=True)
    
    # Timestamps
    joining_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DoctorSchedule(models.Model):
    DAY_CHOICES = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_start = models.TimeField(blank=True, null=True)
    break_end = models.TimeField(blank=True, null=True)
    is_holiday = models.BooleanField(default=False)
    max_appointments = models.IntegerField(default=20)


class DoctorLeave(models.Model):
    LEAVE_TYPES = (
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('emergency', 'Emergency Leave'),
        ('conference', 'Conference'),
        ('other', 'Other'),
    )
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_leaves')
    created_at = models.DateTimeField(auto_now_add=True)


class Patient(models.Model):
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'), 
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), 
        ('O+', 'O+'), ('O-', 'O-'),
    )
    
    MARITAL_STATUS_CHOICES = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    
    # Personal Details
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, default='single')
    occupation = models.CharField(max_length=100, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    emergency_contact_relation = models.CharField(max_length=50)
    emergency_contact_address = models.TextField(blank=True)
    
    # Medical Information
    allergies = models.TextField(blank=True, help_text="List all allergies")
    chronic_diseases = models.TextField(blank=True, help_text="List all chronic diseases")
    current_medications = models.TextField(blank=True)
    past_surgeries = models.TextField(blank=True)
    family_history = models.TextField(blank=True)
    
    # Lifestyle
    smoking_status = models.BooleanField(default=False)
    alcohol_consumption = models.BooleanField(default=False)
    exercise_frequency = models.CharField(max_length=50, blank=True)
    
    # Insurance
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)
    insurance_valid_upto = models.DateField(null=True, blank=True)
    
    # Health Metrics
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    bmi = models.FloatField(null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True)
    
    # Statistics
    total_visits = models.IntegerField(default=0)
    last_visit_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PatientHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='history')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    
    # Visit Details
    visit_date = models.DateTimeField(auto_now_add=True)
    visit_type = models.CharField(max_length=50, choices=[
        ('opd', 'OPD'),
        ('ipd', 'IPD'),
        ('emergency', 'Emergency'),
        ('followup', 'Follow-up'),
    ], default='opd')
    
    # Symptoms and Diagnosis
    chief_complaint = models.TextField()
    symptoms = models.TextField()
    duration_of_symptoms = models.CharField(max_length=100, blank=True)
    diagnosis = models.TextField()
    differential_diagnosis = models.TextField(blank=True)
    
    # Vital Signs
    temperature = models.FloatField(null=True, blank=True, help_text="Body temperature in °C")
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    respiratory_rate = models.IntegerField(null=True, blank=True)
    oxygen_saturation = models.IntegerField(null=True, blank=True)
    
    # Examination
    physical_examination = models.TextField(blank=True)
    investigations = models.TextField(blank=True)
    
    # Treatment
    treatment_plan = models.TextField()
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_instructions = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('referred', 'Referred'),
        ('admitted', 'Admitted'),
    ], default='active')
    
    # Notes
    doctor_notes = models.TextField(blank=True)
    referred_to = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='referred_patients')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PatientDocument(models.Model):
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
    history = models.ForeignKey(PatientHistory, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='patient_documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    )
    
    MODE_CHOICES = (
        ('online', 'Online Booking'),
        ('offline', 'Offline Booking'),
        ('emergency', 'Emergency'),
        ('walk_in', 'Walk-in'),
    )
    
    appointment_id = models.CharField(max_length=50, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    
    # Appointment Details
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    appointment_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='online')
    token_number = models.IntegerField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Booking Details
    booking_date = models.DateTimeField(auto_now_add=True)
    booked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='booked_appointments')
    
    # Cancellation Details
    cancellation_date = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancellation_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Check-in Details
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    
    # Notes
    patient_notes = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class AppointmentQueue(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='queue')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    queue_number = models.IntegerField()
    estimated_wait_time = models.IntegerField(help_text="Estimated wait time in minutes")
    called_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class Medicine(models.Model):
    MEDICINE_TYPE_CHOICES = (
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('ointment', 'Ointment'),
        ('drops', 'Drops'),
        ('inhaler', 'Inhaler'),
        ('other', 'Other'),
    )
    
    CATEGORY_CHOICES = (
        ('antibiotic', 'Antibiotic'),
        ('analgesic', 'Analgesic'),
        ('antihypertensive', 'Antihypertensive'),
        ('antidiabetic', 'Antidiabetic'),
        ('antidepressant', 'Antidepressant'),
        ('antihistamine', 'Antihistamine'),
        ('vitamin', 'Vitamin'),
        ('vaccine', 'Vaccine'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200)
    brand_name = models.CharField(max_length=200, blank=True)
    manufacturer = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    medicine_type = models.CharField(max_length=20, choices=MEDICINE_TYPE_CHOICES)
    
    # Composition
    composition = models.TextField(help_text="Active ingredients and their quantities")
    strength = models.CharField(max_length=100, help_text="e.g., 500mg, 10ml")
    
    # Usage
    dosage_form = models.CharField(max_length=100)
    standard_dosage = models.TextField(help_text="Standard dosage instructions")
    route_of_administration = models.CharField(max_length=100, default="Oral")
    
    # Precautions
    side_effects = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    warnings = models.TextField(blank=True)
    
    # Regulatory
    is_prescription_required = models.BooleanField(default=True)
    schedule = models.CharField(max_length=10, choices=[
        ('H', 'Schedule H'),
        ('X', 'Schedule X'),
        ('G', 'Schedule G'),
        ('none', 'No Schedule'),
    ], default='none')
    
    # Stock Information
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)


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
    
    patient_history = models.ForeignKey(PatientHistory, on_delete=models.CASCADE, related_name='prescriptions')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    
    # Dosage
    dosage = models.CharField(max_length=100, help_text="e.g., 1 tablet")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    duration_value = models.IntegerField()
    duration_unit = models.CharField(max_length=10, choices=DURATION_UNIT_CHOICES)
    
    # Instructions
    instructions = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True, help_text="Special instructions like take with food")
    
    # Additional
    is_refillable = models.BooleanField(default=False)
    refill_count = models.IntegerField(default=0)
    refills_used = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    dispensed = models.BooleanField(default=False)
    dispensed_date = models.DateTimeField(null=True, blank=True)
    dispensed_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    prescribed_date = models.DateTimeField(auto_now_add=True)