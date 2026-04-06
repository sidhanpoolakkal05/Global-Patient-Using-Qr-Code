from django.contrib import admin
from .models import Appointment, AppointmentQueue

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_id', 'patient', 'doctor', 'hospital', 'appointment_date', 'status', 'payment_status')
    list_filter = ('status', 'payment_status', 'appointment_mode', 'appointment_date')
    search_fields = ('appointment_id', 'patient__username', 'doctor__username', 'hospital__name')
    readonly_fields = ('appointment_id', 'created_at', 'updated_at')

@admin.register(AppointmentQueue)
class AppointmentQueueAdmin(admin.ModelAdmin):
    list_display = ('queue_number', 'doctor', 'appointment', 'called_at', 'completed_at')
    list_filter = ('doctor', 'called_at', 'completed_at')
    search_fields = ('appointment__appointment_id', 'doctor__username')
