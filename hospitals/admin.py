from django.contrib import admin
from .models import (
    Hospital, HospitalSettings, DoctorSlot, 
    DoctorSchedule, DoctorLeave, Medicine, MedicineStock
)

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'hospital_type', 'location', 'is_verified', 'is_active', 'rating')
    list_filter = ('hospital_type', 'is_verified', 'is_active')
    search_fields = ('name', 'registration_number', 'contact', 'email')

@admin.register(HospitalSettings)
class HospitalSettingsAdmin(admin.ModelAdmin):
    list_display = ('hospital', 'online_seats')
    search_fields = ('hospital__name',)

@admin.register(DoctorSlot)
class DoctorSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'hospital', 'consultation_fee', 'start_time', 'end_time')
    search_fields = ('doctor__username', 'hospital__name')

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'hospital', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'hospital')
    search_fields = ('doctor__username',)

@admin.register(DoctorLeave)
class DoctorLeaveAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'leave_type', 'start_date', 'end_date', 'is_approved')
    list_filter = ('leave_type', 'is_approved')
    search_fields = ('doctor__username',)

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'medicine_type', 'unit_price', 'stock_quantity')
    list_filter = ('category', 'medicine_type', 'is_prescription_required')
    search_fields = ('name', 'generic_name', 'brand_name')

@admin.register(MedicineStock)
class MedicineStockAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'hospital', 'batch_number', 'expiry_date', 'quantity')
    list_filter = ('hospital', 'expiry_date')
    search_fields = ('medicine__name', 'batch_number')
