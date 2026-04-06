from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Hospital(models.Model):
    HOSPITAL_TYPE_CHOICES = (
        ('general', 'General Hospital'),
        ('specialty', 'Specialty Hospital'),
        ('teaching', 'Teaching Hospital'),
        ('clinic', 'Clinic'),
        ('research', 'Research Hospital'),
    )

    name = models.CharField(max_length=255)
    hospital_type = models.CharField(max_length=20, choices=HOSPITAL_TYPE_CHOICES, default='general')
    registration_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    contact = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(unique=True)
    website = models.URLField(blank=True)
    address = models.TextField()
    location = models.CharField(max_length=255)

    # Infrastructure
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

    # Status & Rating
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class HospitalSettings(models.Model):
    hospital = models.OneToOneField(Hospital, on_delete=models.CASCADE, related_name='settings')
    # Online seats available per day for the hospital
    online_seats = models.PositiveIntegerField(default=20)

    def __str__(self):
        return f"Settings for {self.hospital.name}"


class DoctorProfile(models.Model):
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

    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    qualification = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(default=0)
    registration_number = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    languages = models.CharField(max_length=200, default="English")

    def __str__(self):
        return f"Dr. {self.user.username} - {self.specialization}"


class StaffProfile(models.Model):
    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, related_name='staff_profile')
    department = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Staff: {self.user.username} - {self.department}"


class DoctorSlot(models.Model):
    """Stores per-doctor consultation fee and available time slots for a hospital."""
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctor_slots')
    doctor = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='slots')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor.username} @ {self.hospital.name} ({self.start_time} - {self.end_time})"


class DoctorSchedule(models.Model):
    """Weekly recurring schedule for a doctor at a hospital."""
    DAY_CHOICES = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    ]

    doctor = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='schedules')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='schedules', null=True, blank=True)
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_start = models.TimeField(blank=True, null=True)
    break_end = models.TimeField(blank=True, null=True)
    is_holiday = models.BooleanField(default=False)
    max_appointments = models.IntegerField(default=20)

    class Meta:
        unique_together = ('doctor', 'hospital', 'day_of_week')
        ordering = ['day_of_week']

    def __str__(self):
        return f"Dr.{self.doctor.username} - {self.day_of_week} ({self.start_time}-{self.end_time})"


class DoctorLeave(models.Model):
    """Tracks leave applications for doctors."""
    LEAVE_TYPES = (
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('emergency', 'Emergency Leave'),
        ('conference', 'Conference'),
        ('other', 'Other'),
    )

    doctor = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='leaves')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctor_leaves', null=True, blank=True)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_leaves'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr.{self.doctor.username} - {self.leave_type} ({self.start_date} to {self.end_date})"


class Medicine(models.Model):
    """Comprehensive medicine/drug database managed globally."""
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

    SCHEDULE_CHOICES = (
        ('H', 'Schedule H'),
        ('X', 'Schedule X'),
        ('G', 'Schedule G'),
        ('none', 'No Schedule'),
    )

    name = models.CharField(max_length=255)
    generic_name = models.CharField(max_length=200, blank=True)
    brand_name = models.CharField(max_length=200, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=100, blank=True, choices=CATEGORY_CHOICES)
    medicine_type = models.CharField(max_length=20, choices=MEDICINE_TYPE_CHOICES, blank=True)

    # Composition
    composition = models.TextField(blank=True, help_text="Active ingredients and quantities")
    description = models.TextField(blank=True, help_text="General description or notes")
    strength = models.CharField(max_length=100, blank=True, help_text="e.g., 500mg")
    unit = models.CharField(max_length=50, blank=True, help_text="e.g., Strip, Bottle, Tablet")

    # Usage
    standard_dosage = models.TextField(blank=True)
    route_of_administration = models.CharField(max_length=100, default="Oral")

    # Precautions
    side_effects = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    warnings = models.TextField(blank=True)

    # Regulatory
    is_prescription_required = models.BooleanField(default=True)
    schedule = models.CharField(max_length=10, choices=SCHEDULE_CHOICES, default='none')

    # Stock
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    expiry_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# Backward-compatibility alias so existing code referencing MedicineMaster still works
MedicineMaster = Medicine


class MedicineStock(models.Model):
    """Per-hospital medicine stock tracking."""
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='stocks')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='medicine_stocks')
    batch_number = models.CharField(max_length=100)
    expiry_date = models.DateField()
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    supplier = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['expiry_date']

    def __str__(self):
        return f"{self.medicine.name} - {self.hospital.name} (Batch: {self.batch_number})"
