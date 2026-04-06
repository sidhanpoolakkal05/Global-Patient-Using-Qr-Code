# 🏥 MediScan: Seamless QR-Based Hospital Management System

[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![REST API](https://img.shields.io/badge/REST-API-0F6E56?style=for-the-badge)](https://www.django-rest-framework.org/)
[![QR Scanning](https://img.shields.io/badge/QR-Scanning-0F6E56?style=for-the-badge)](https://github.com/mebjas/html5-qrcode)

**MediScan** is a modern, full-stack Hospital Management System (HMS) designed to revolutionize patient care through secure QR technology. It streamlines patient registration, medical history access, and prescription management into a seamless, paperless workflow.

---

## ✨ Key Features

- **🚀 Instant QR Registration**: Generate unique medical QR codes for patients within seconds.
- **🛡️ Secure Data Protection**: Role-based access control (Global Admin, Hospital Admin, Doctor, Staff, Patient) ensures sensitive data is only seen by authorized personnel.
- **📖 Centralized Medical Records**: Instant access to patient history, current medications, and past consultations via a simple scan.
- **⚡ Streamlined Prescriptions**: Digitize and store prescriptions directly linked to the patient's identity via the "Prescription Train" system.
- **📊 Hospital Dashboards**: Real-time analytics for monitoring registrations, appointments, and consultations.
- **🎨 Premium UI/UX**: Fast, responsive, and animated user interface built with Vanilla CSS and modern web standards.

---

## 🛠️ Project Architecture

MediScan is built as a unified Django ecosystem:
- **Core**: Django 5.0 + Django REST Framework
- **Frontend**: Integrated Django Templates with a robust Vanilla CSS design system.
- **Authentication**: JWT-based secure sessions.
- **Features**: QR Code generation/scanning, Real-time appointment queue, and clinical treatment desk.

---

## 🚀 Getting Started

### Prerequisites
- [Python](https://www.python.org/) (v3.10 or higher)
- [Git](https://git-scm.com/)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/abhi963007/mediscan.git
   cd mediscan
   ```

2. **Setup Backend**
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate it (Windows)
   .\venv\Scripts\activate
   
   # Activate it (macOS/Linux)
   source venv/bin/activate
   
   # Install Django & dependencies
   pip install django djangorestframework django-cors-headers djangorestframework-simplejwt qrcode[pil]
   ```

3. **Initialize the Database**
   ```bash
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   
   # Create the Global Administrator account
   # Use username 'admin' and password 'admin' for default setup
   python manage.py createsuperuser
   ```

4. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```

---

## 👥 Roles & Access Control

| Role | Access Level |
| :--- | :--- |
| **Global Admin** | Full system oversight, hospital registration, and drug master management. |
| **Hospital Admin** | Manage hospital staff (CRUD), appointments, and institution settings. |
| **Doctor** | Manage clinical queue, scan patient QRs, and write digital prescriptions. |
| **Receptionist** | Register new patients, scan QR cards for check-in, and manage slots. |
| **Patient** | View own digital health card, prescription history, and profile. |

---

## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📧 Support & Contact

- **Maintained by**: [Abhimanyu](https://github.com/abhi963007)
- **Project Link**: [https://github.com/abhi963007/mediscan](https://github.com/abhi963007/mediscan)

Built with ❤️ for Healthcare Providers.
