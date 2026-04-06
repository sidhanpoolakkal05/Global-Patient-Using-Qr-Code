from django.shortcuts import render, redirect
from django.views import View


# ─────────────────────────────────────────
# Helper context data for static pages
# ─────────────────────────────────────────

FEATURES_DATA = [
    {"icon": "qr-code",        "bg": "#ECFDF5", "color": "#0F6E56", "title": "QR Health Cards",          "desc": "Every patient gets a unique QR health card that stores their complete medical profile. Scan it at any MediScan hospital instantly."},
    {"icon": "shield-check",   "bg": "#EFF6FF", "color": "#2563EB", "title": "Secure Records",            "desc": "All patient data is encrypted and stored securely. Role-based access ensures only authorised personnel can view sensitive records."},
    {"icon": "calendar",       "bg": "#FEF3C7", "color": "#D97706", "title": "Smart Appointments",        "desc": "Patients can book appointments online. Receptionists can view the queue and doctors see their schedule in real time."},
    {"icon": "stethoscope",    "bg": "#F3F4F6", "color": "#6B7280", "title": "Doctor Treatment Desk",     "desc": "Doctors log diagnoses, prescribe medicines from the master catalog, and set follow-up reminders all in one place."},
    {"icon": "pill",           "bg": "#FEF2F2", "color": "#DC2626", "title": "Medicine Catalog",          "desc": "A centrally managed medicine master maintained by the global admin ensures consistent, accurate prescriptions."},
    {"icon": "building-2",     "bg": "#F5F3FF", "color": "#7C3AED", "title": "Multi-Hospital Support",   "desc": "Patients can visit any registered hospital and staff can instantly access their health record by scanning their QR card."},
]

MODULES_DATA = [
    {"icon": "shield-check",   "bg": "#ECFDF5", "color": "#0F6E56", "title": "Global Admin Module",       "desc": "Manage all hospitals and the medicine catalog from a single control panel. Full visibility across the entire system."},
    {"icon": "building-2",     "bg": "#EFF6FF", "color": "#2563EB", "title": "Hospital Admin Module",     "desc": "Hospital administrators manage their staff, configure doctor slots, and maintain hospital profile settings."},
    {"icon": "scan",           "bg": "#FEF3C7", "color": "#D97706", "title": "Receptionist Module",       "desc": "Receptionists register new patients, scan QR cards, book appointments, and manage the daily queue."},
    {"icon": "stethoscope",    "bg": "#FEF2F2", "color": "#DC2626", "title": "Doctor Module",             "desc": "Doctors view their appointment queue, access patient medical history, prescribe medicines, and log treatment notes."},
    {"icon": "qr-code",        "bg": "#F5F3FF", "color": "#7C3AED", "title": "Patient Module",            "desc": "Patients manage their digital health card, book appointments at any hospital, and view their full medical history."},
]

FAQS_DATA = [
    {"q": "How do I get a QR health card?", "a": "Register as a patient either online at /register/ or at any MediScan hospital reception desk. A unique QR health card is automatically generated for you."},
    {"q": "Can I use my card at any hospital?", "a": "Yes. Any hospital registered in the MediScan system can scan your QR card and access your health record instantly."},
    {"q": "Is my medical data secure?", "a": "Absolutely. All data is encrypted, access is role-based, and only authorised healthcare personnel can view your records."},
    {"q": "How do I book an appointment?", "a": "Log in to your patient dashboard and go to 'Book Appointment'. Browse available doctor slots and confirm your booking."},
    {"q": "Can doctors or receptionists register themselves?", "a": "No. Doctor and receptionist accounts are created by the Hospital Administrator. Contact your hospital admin to create a staff account."},
    {"q": "What if I forget my password?", "a": "Contact your hospital receptionist or system administrator to reset your password."},
]

CONTACTS_DATA = [
    {"icon": "mail",     "bg": "#ECFDF5", "color": "#0F6E56", "title": "Email Support", "desc": "Send us an email and we'll respond within 24 hours.", "href": "mailto:mediscan.official.hms@gmail.com", "link": "mediscan.official.hms@gmail.com"},
    {"icon": "phone",    "bg": "#EFF6FF", "color": "#2563EB", "title": "Phone Support", "desc": "Available Monday–Friday, 9AM to 6PM IST.", "href": "tel:+911800000000", "link": "+91 1800 000 000"},
    {"icon": "life-buoy","bg": "#FEF3C7", "color": "#D97706", "title": "Help Center",   "desc": "Browse our documentation and FAQs below.", "href": "#", "link": "Browse FAQs ↓"},
]

SCAN_INSTRUCTIONS = [
    "Ask the patient to show their MediScan QR card",
    "Scan the QR code or type the UHID manually",
    "Review patient details and medical history",
    "Select an available doctor slot to book an appointment",
]

REGISTER_PATIENT_TIPS = [
    "Verify the patient's ID before registration",
    "Use a strong password (share it securely)",
    "Double-check blood group and phone number",
    "Medical history helps doctors provide better care",
]


# ─────────────────────────────────────────
# Public views
# ─────────────────────────────────────────

class LandingView(View):
    def get(self, request):
        context = {
            'stats': [
                {'value': '150+', 'label': 'Hospitals'},
                {'value': '50k+', 'label': 'Patients'},
                {'value': '2.5k+', 'label': 'Doctors'},
                {'value': '99.9%', 'label': 'Uptime'},
            ],
            'features': FEATURES_DATA[:3] # Show first 3 on landing
        }
        return render(request, 'frontend/landing.html', context)


class LoginView(View):
    def get(self, request):
        context = {
            'benefits': [
                'QR patient cards in seconds',
                'Unified medical records',
                'Real-time appointment tracking'
            ]
        }
        return render(request, 'frontend/login.html', context)


class RegisterView(View):
    def get(self, request):
        return render(request, 'frontend/register.html')


class ForgotPasswordView(View):
    def get(self, request):
        return render(request, 'frontend/forgot_password.html')


class FeaturesView(View):
    def get(self, request):
        return render(request, 'frontend/features.html', {'features': FEATURES_DATA})


class ModulesView(View):
    def get(self, request):
        return render(request, 'frontend/modules.html', {'modules': MODULES_DATA})


class SupportView(View):
    def get(self, request):
        return render(request, 'frontend/support.html', {
            'faqs': FAQS_DATA,
            'contacts': CONTACTS_DATA,
        })


# ─────────────────────────────────────────
# Dashboard redirect (role resolved client-side via JS)
# ─────────────────────────────────────────

class DashboardRedirectView(View):
    """Client-side auth guard reads localStorage and redirects by role."""
    def get(self, request):
        return render(request, 'frontend/dashboard_redirect.html')


# ─────────────────────────────────────────
# Admin dashboard views
# ─────────────────────────────────────────

class AdminOverviewView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/admin/overview.html',
                      {'allowed_roles': "['admin']"})


class AdminHospitalsView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/admin/hospitals.html',
                      {'allowed_roles': "['admin']"})


class AdminMedicinesView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/admin/medicines.html',
                      {'allowed_roles': "['admin']"})


# ─────────────────────────────────────────
# Hospital admin dashboard views
# ─────────────────────────────────────────

class HospitalOverviewView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/hospital/overview.html',
                      {'allowed_roles': "['hospital_admin']"})


class HospitalStaffView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/hospital/staff.html',
                      {'allowed_roles': "['hospital_admin']"})


class HospitalSlotsView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/hospital/slots.html',
                      {'allowed_roles': "['hospital_admin']"})


class HospitalSettingsView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/hospital/settings.html',
                      {'allowed_roles': "['hospital_admin']"})


# ─────────────────────────────────────────
# Receptionist / Staff dashboard views
# ─────────────────────────────────────────

class StaffOverviewView(View):
    def get(self, request):
        context = {
            'allowed_roles': "['receptionist']",
            'quick_actions': [
                {
                    'title': 'Register Patient',
                    'url': '/dashboard/staff/register/',
                    'icon': 'user-plus',
                    'bg': '#ECFDF5',
                    'color': '#0F6E56',
                    'desc': 'Quick registration'
                },
                {
                    'title': 'Scan QR Card',
                    'url': '/dashboard/staff/scan/',
                    'icon': 'scan',
                    'bg': '#EFF6FF',
                    'color': '#2563EB',
                    'desc': 'Instant check-in'
                },
                {
                    'title': 'View Appointments',
                    'url': '/dashboard/staff/appointments/',
                    'icon': 'calendar',
                    'bg': '#FEF3C7',
                    'color': '#D97706',
                    'desc': 'Daily schedule'
                },
            ]
        }
        return render(request, 'frontend/dashboard/staff/overview.html', context)


class StaffRegisterPatientView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/staff/register_patient.html', {
            'allowed_roles': "['receptionist']",
            'tips': REGISTER_PATIENT_TIPS,
        })


class StaffPatientsView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/staff/patients.html',
                      {'allowed_roles': "['receptionist']"})


class StaffScanView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/staff/scan.html', {
            'allowed_roles': "['receptionist']",
            'instructions': SCAN_INSTRUCTIONS,
        })


class StaffAppointmentsView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/staff/appointments.html',
                      {'allowed_roles': "['receptionist']"})


class StaffSlotsView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/staff/slots.html',
                      {'allowed_roles': "['receptionist']"})


# ─────────────────────────────────────────
# Doctor dashboard views
# ─────────────────────────────────────────

class DoctorOverviewView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/doctor/overview.html',
                      {'allowed_roles': "['doctor']"})


class DoctorAppointmentsView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/doctor/appointments.html',
                      {'allowed_roles': "['doctor']"})


class DoctorTreatmentView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/doctor/treatment.html',
                      {'allowed_roles': "['doctor']"})


# ─────────────────────────────────────────
# Patient dashboard views
# ─────────────────────────────────────────

class PatientOverviewView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/patient/overview.html',
                      {'allowed_roles': "['patient']"})


class PatientBookView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/patient/book.html',
                      {'allowed_roles': "['patient']"})


class PatientHistoryView(View):
    def get(self, request):
        return render(request, 'frontend/dashboard/patient/history.html',
                      {'allowed_roles': "['patient']"})
