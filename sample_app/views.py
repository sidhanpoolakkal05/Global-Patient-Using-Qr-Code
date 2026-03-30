from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .models import User, Doctor, Hospital

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user.user_type == 'hospital':
                return render(request, 'hospital_dashboard.html')
            elif user.user_type == 'doctor':
                return render(request, 'doctor_dashboard.html')
            elif user.user_type == 'staff':
                return render(request, 'staff_dashboard.html')
            elif user.user_type == 'patient':
                return render(request, 'patient_dashboard.html')
        else:
            return HttpResponse("Invalid credentials. Please try again.")
    return render(request, 'login.html')
        
def doctor_register(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password')
        name = (request.POST.get('name') or '').strip()

        if not username:
            if email:
                username = email.split('@')[0]
            else:
                return HttpResponse("Username or email is required", status=400)

        if not password:
            return HttpResponse("Password is required", status=400)

        if not email:
            return HttpResponse("Email is required", status=400)

        phone = request.POST.get('phone') or ''

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            user_type='doctor',
            phone=phone,
            first_name=name,
        )

        hospital_id = request.POST.get('hospital_id')
        if not hospital_id:
            return HttpResponse("Hospital ID is required", status=400)

        Doctor.objects.create(
            user=user,
            hospital_id=hospital_id,
            specialization=request.POST.get('specialization', ''),
            consultation_fee=500,
            available_seats=50,
        )
        return HttpResponse("Doctor registered successfully..")
    hospitals = Hospital.objects.all()
    return render(request, 'doctor_register.html', {'hospitals': hospitals})

def hospital_register(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password')
        name = (request.POST.get('name') or '').strip()

        if not username:
            if email:
                username = email.split('@')[0]
            else:
                return HttpResponse("Username or email is required", status=400)

        if not password:
            return HttpResponse("Password is required", status=400)

        if not email:
            return HttpResponse("Email is required", status=400)

        phone = request.POST.get('phone')
        if not phone:
            return HttpResponse("Phone is required", status=400)

        city = request.POST.get('city')
        if not city:
            city = ''

        # user model uses first_name/last_name, not name; store as first_name
        first_name = name

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            user_type='hospital',
            phone=phone,
            address=request.POST.get('address', ''),
            city=city,
            state=request.POST.get('state', ''),
            country=request.POST.get('country', ''),
            pincode=request.POST.get('pincode', ''),
            first_name=first_name,
        )

        user.generate_qr_code()  # Generate QR code for the user

        Hospital.objects.create(
            user=user,
            name=name,
            email=email,
            registration_number=request.POST.get('reg_no') or request.POST.get('registration_number', ''),
            address=request.POST.get('address', ''),
            city=city,
            state=request.POST.get('state', ''),
            country=request.POST.get('country', ''),
            pincode=request.POST.get('pincode', ''),
            phone=phone,
            hospital_type=request.POST.get('type', 'general'),
        )

        return HttpResponse("Hospital registered successfully..")
    return render(request, 'hospital_register.html')