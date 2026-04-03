# 🏥 MediCare HMS — Hospital Management System

A professional, full-stack **Hospital Management System** built with Django 6, featuring role-based dashboards, AI-powered pre-consultation via Google Gemini, automated PDF billing, and a premium SaaS-style UI.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Role-Based Auth** | Admin, Doctor, Patient — each with a dedicated dashboard |
| **Appointment System** | Book, Approve, Complete — with Online / Offline types |
| **Join Meeting Button** | Appears on Patient dashboard *only* when appointment is Online + Approved |
| **AI Doctor (Gemini)** | Symptom analysis → Urgency level, Specialist recommendation, Clinical summary |
| **Medical Vault** | Patients upload & store lab reports, prescriptions, scans |
| **Auto PDF Billing** | ReportLab invoice generated automatically when appointment is completed |
| **Premium UI** | Tailwind CSS, Deep Navy `#0f172a`, Glassmorphism cards, Inter font, skeleton loader |
| **Fixed Sidebar** | Responsive with mobile toggle, role-aware navigation |

---

## 🖼️ Tech Stack

- **Backend:** Django 6, Python
- **Database:** SQLite (dev) — easily swappable with PostgreSQL
- **AI:** Google Gemini 1.5 Flash via `google-generativeai`
- **PDF:** ReportLab
- **UI:** Tailwind CSS (CDN), vanilla CSS, Inter font
- **Auth:** Django's `AbstractUser` with custom `role` field

---

## 📁 Project Structure

```
Hospital Management/
├── core/                  # Django project config (settings, urls)
├── users/                 # Custom user model, auth views, Doctor profile
├── hospital/              # Appointments, Medical Records, Billing, dashboards
├── api/                   # Gemini AI service + AI Doctor view
├── templates/             # Root templates folder
│   ├── base.html          # Sidebar shell
│   ├── partials/          # Role-specific nav includes
│   ├── users/             # login.html, register.html
│   ├── hospital/          # patient/doctor/admin dashboards, booking, records
│   └── api/               # ai_doctor.html
├── static/
│   ├── css/custom.css
│   └── js/sidebar.js, ai_loader.js
├── media/                 # User uploads (gitignored)
├── .env                   # Secrets (gitignored — see .env.example)
└── manage.py
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/medicare-hms.git
cd medicare-hms
```

### 2. Create & activate virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install django google-generativeai reportlab pillow python-decouple
```

### 4. Configure environment
```bash
cp .env.example .env
```
Edit `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
GEMINI_API_KEY=your_gemini_api_key_here
```
> Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com/app/apikey)

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Start the server
```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000** — you'll be redirected to the login page.

---

## 👥 User Roles

| Role | Default Dashboard | How to Create |
|---|---|---|
| **Admin** | `/hospital/admin-panel/` | `createsuperuser` → set role to ADMIN in Django admin |
| **Doctor** | `/hospital/doctor/` | Register at `/users/register/?role=doctor` |
| **Patient** | `/hospital/dashboard/` | Register at `/users/register/?role=patient` |

---

## 🤖 AI Doctor

The AI Doctor uses **Google Gemini 1.5 Flash** to analyze patient symptoms and return a structured **Pre-Consultation Report**:

- 🚨 **Urgency Level** (LOW / MEDIUM / HIGH / CRITICAL)
- 🩺 **Recommended Specialist** with reasoning
- 📋 **Clinical Summary**
- 🔬 **Suggested Tests**
- 💡 **Lifestyle Tips**

A professional skeleton loader animation plays while Gemini is "thinking". If no API key is configured, a graceful demo report is returned.

---

## 📄 PDF Billing

When a doctor marks an appointment as **Completed**, the system automatically:
1. Creates a `Billing` record with the doctor's consultation fee
2. Generates a professional A4 PDF invoice using ReportLab
3. Makes it available for the patient to download from their dashboard

---

## 🔒 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Django secret key |
| `DEBUG` | ✅ | `True` for development |
| `GEMINI_API_KEY` | ⚡ Optional | Google Gemini API key for AI Doctor |

---

## 📦 Key Dependencies

```
django
google-generativeai
reportlab
pillow
python-decouple
```

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

> Built with ❤️ using Django & Google Gemini
