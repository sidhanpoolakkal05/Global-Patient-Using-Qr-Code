from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('receptionist', 'Receptionist'),
        ('hospital_admin', 'Hospital Admin'),
        ('admin', 'Admin'),
    )
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    # Existing roles
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    is_approved = models.BooleanField(default=False)

    # Enriched contact & profile info
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Tracking
    is_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Links doctor / receptionist / hospital_admin to a specific hospital.
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members',
    )

    def save(self, *args, **kwargs):
        # Ensure superusers have the 'admin' role and are approved
        if self.is_superuser:
            self.role = 'admin'
            self.is_approved = True
        elif self.role in ['patient', 'admin']:
            self.is_approved = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

    def get_full_name(self):
        full_name = super().get_full_name()
        return full_name.strip() or self.username
