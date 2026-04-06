from django.contrib import admin
from .models import Patient, Consultation, Prescription, PatientDocument

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('uhid', 'full_name', 'gender', 'age', 'blood_group', 'phone', 'email')
    search_fields = ('uhid', 'full_name', 'phone', 'email')
    list_filter = ('gender', 'blood_group')

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'hospital', 'consultation_date', 'status', 'visit_type')
    list_filter = ('status', 'visit_type', 'consultation_date')
    search_fields = ('patient__full_name', 'doctor__username', 'diagnosis')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('medicine_name', 'consultation', 'dosage', 'frequency', 'dispensed')
    list_filter = ('dispensed', 'prescribed_date')
    search_fields = ('medicine_name', 'consultation__patient__full_name')

@admin.register(PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'document_type', 'upload_date')
    list_filter = ('document_type', 'upload_date')
    search_fields = ('title', 'patient__full_name')
