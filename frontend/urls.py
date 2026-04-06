from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    # ── Public pages ──────────────────────────────────────────────
    path('',          views.LandingView.as_view(),   name='landing'),
    path('login/',    views.LoginView.as_view(),     name='login'),
    path('register/', views.RegisterView.as_view(),  name='register'),
    path('features/', views.FeaturesView.as_view(),  name='features'),
    path('modules/',  views.ModulesView.as_view(),   name='modules'),
    path('support/',  views.SupportView.as_view(),   name='support'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),

    # ── Dashboard root (client-side redirect by role) ─────────────
    path('dashboard/', views.DashboardRedirectView.as_view(), name='dashboard'),

    # ── Global Admin ──────────────────────────────────────────────
    path('dashboard/admin/',             views.AdminOverviewView.as_view(),   name='admin-overview'),
    path('dashboard/admin/hospitals/',   views.AdminHospitalsView.as_view(),  name='admin-hospitals'),
    path('dashboard/admin/medicines/',   views.AdminMedicinesView.as_view(),  name='admin-medicines'),

    # ── Hospital Admin ────────────────────────────────────────────
    path('dashboard/hospital/',          views.HospitalOverviewView.as_view(),  name='hospital-overview'),
    path('dashboard/hospital/staff/',    views.HospitalStaffView.as_view(),     name='hospital-staff'),
    path('dashboard/hospital/slots/',    views.HospitalSlotsView.as_view(),     name='hospital-slots'),
    path('dashboard/hospital/settings/', views.HospitalSettingsView.as_view(),  name='hospital-settings'),

    # ── Receptionist / Staff ──────────────────────────────────────
    path('dashboard/staff/',              views.StaffOverviewView.as_view(),        name='staff-overview'),
    path('dashboard/staff/register/',     views.StaffRegisterPatientView.as_view(), name='staff-register'),
    path('dashboard/staff/patients/',     views.StaffPatientsView.as_view(),        name='staff-patients'),
    path('dashboard/staff/scan/',         views.StaffScanView.as_view(),            name='staff-scan'),
    path('dashboard/staff/appointments/', views.StaffAppointmentsView.as_view(),    name='staff-appointments'),
    path('dashboard/staff/slots/',        views.StaffSlotsView.as_view(),           name='staff-slots'),

    # ── Doctor ────────────────────────────────────────────────────
    path('dashboard/doctor/',              views.DoctorOverviewView.as_view(),      name='doctor-overview'),
    path('dashboard/doctor/appointments/', views.DoctorAppointmentsView.as_view(),  name='doctor-appointments'),
    path('dashboard/doctor/treatment/',    views.DoctorTreatmentView.as_view(),     name='doctor-treatment'),

    # ── Patient ───────────────────────────────────────────────────
    path('dashboard/patient/',         views.PatientOverviewView.as_view(), name='patient-overview'),
    path('dashboard/patient/book/',    views.PatientBookView.as_view(),     name='patient-book'),
    path('dashboard/patient/history/', views.PatientHistoryView.as_view(),  name='patient-history'),
]
