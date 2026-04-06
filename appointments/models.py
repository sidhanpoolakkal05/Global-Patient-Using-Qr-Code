from django.db import models
from django.conf import settings
import uuid


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]
    MODE_CHOICES = (
        ('online', 'Online Booking'),
        ('offline', 'Offline Booking'),
        ('emergency', 'Emergency'),
        ('walk_in', 'Walk-in'),
    )

    appointment_id = models.CharField(max_length=50, unique=True, editable=False, blank=True)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_as_doctor')
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.CASCADE, related_name='appointments')

    # Appointment details
    appointment_date = models.DateField()
    time_slot = models.TimeField()  # kept for backward compatibility
    appointment_time = models.TimeField(null=True, blank=True)  # alias
    appointment_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='online')
    token_number = models.IntegerField(null=True, blank=True)

    # Status & payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    payment_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    # Booking meta
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='booked_appointments'
    )

    # Cancellation
    cancellation_date = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancellation_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rejection_reason = models.TextField(blank=True, null=True)  # kept from original

    # Check-in/out
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True, null=True)
    patient_notes = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    suggestion = models.TextField(blank=True, null=True)  # kept from original

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['appointment_date', 'time_slot']

    def save(self, *args, **kwargs):
        if not self.appointment_id:
            self.appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
        # Sync time_slot and appointment_time
        if self.appointment_time and not self.time_slot:
            self.time_slot = self.appointment_time
        elif self.time_slot and not self.appointment_time:
            self.appointment_time = self.time_slot
        # Sync fee and consultation_fee
        if self.consultation_fee and not self.fee:
            self.fee = self.consultation_fee
        elif self.fee and not self.consultation_fee:
            self.consultation_fee = self.fee
        # Calculate total_amount
        if not self.total_amount:
            self.total_amount = (self.consultation_fee or self.fee) - self.discount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient.username} → Dr.{self.doctor.username} on {self.appointment_date}"


class AppointmentQueue(models.Model):
    """Real-time queue tracking for doctor appointments at a hospital."""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='queue')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='queue_entries')
    queue_number = models.IntegerField()
    estimated_wait_time = models.IntegerField(help_text="Estimated wait time in minutes", default=0)
    called_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['queue_number']

    def __str__(self):
        return f"Queue #{self.queue_number} - {self.appointment}"
