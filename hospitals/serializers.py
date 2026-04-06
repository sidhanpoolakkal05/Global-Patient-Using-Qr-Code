from rest_framework import serializers
from .models import (
    Hospital, HospitalSettings, DoctorSlot,
    Medicine, MedicineStock, DoctorSchedule, DoctorLeave
)


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'
        read_only_fields = ('is_verified', 'created_at', 'updated_at')


class HospitalSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalSettings
        fields = '__all__'


class DoctorSlotSerializer(serializers.ModelSerializer):
    doctor_username = serializers.CharField(source='doctor.username', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)

    class Meta:
        model = DoctorSlot
        fields = '__all__'
        read_only_fields = ('hospital',)


class DoctorScheduleSerializer(serializers.ModelSerializer):
    doctor_username = serializers.CharField(source='doctor.username', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)

    class Meta:
        model = DoctorSchedule
        fields = '__all__'
        read_only_fields = ('hospital', 'doctor')


class DoctorLeaveSerializer(serializers.ModelSerializer):
    doctor_username = serializers.CharField(source='doctor.username', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)

    class Meta:
        model = DoctorLeave
        fields = '__all__'
        read_only_fields = ('is_approved', 'approved_by', 'doctor', 'hospital')


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'
        read_only_fields = ('added_at', 'updated_at', 'added_by')


# Alias so any code importing MedicineMasterSerializer still works
MedicineMasterSerializer = MedicineSerializer


class MedicineStockSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)

    class Meta:
        model = MedicineStock
        fields = '__all__'
        read_only_fields = ('hospital',)
