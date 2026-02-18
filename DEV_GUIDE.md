# Dev Guide — CKLab Management System

คู่มือสำหรับนักพัฒนาในทีม อธิบายโครงสร้างโปรเจกต์ สถาปัตยกรรม และแนวทางการเขียนโค้ด

---

## 1. Project Structure

```
CheckinLabManagement/
├── cklab_project/                # Django project config
│   ├── settings.py               # Database, apps, middleware, auth redirects
│   ├── urls.py                   # Root URL → include('lab_management.urls')
│   ├── wsgi.py
│   └── asgi.py
│
├── lab_management/               # Main application
│   ├── models.py                 # SiteConfig, Software, Booking, Status, Computer, UsageLog
│   ├── views/                    # Class-Based Views (CBV) — แยกไฟล์ตามผู้รับผิดชอบ
│   │   ├── __init__.py           # Re-export ทุก class (urls.py ใช้งานได้เหมือนเดิม)
│   │   ├── kiosk.py              # ปภังกร: IndexView, ConfirmView, TimerView, FeedbackView
│   │   ├── monitor.py            # ธนสิทธิ์: AdminMonitorView, ApiMonitorDataView
│   │   ├── booking.py            # อัษฎาวุธ: AdminBookingView, AdminImportBookingView
│   │   ├── manage_pc.py          # ณัฐกรณ์: AdminManagePcView
│   │   ├── software.py           # ลลิดา: AdminSoftwareView
│   │   ├── report.py             # เขมมิกา: AdminReportView, AdminReportExportView
│   │   └── config.py             # ภานุวัฒน์: AdminConfigView
│   ├── urls.py                   # URL patterns ทั้งหมด
│   ├── admin.py                  # Django admin registration
│   ├── apps.py
│   ├── tests.py
│   ├── migrations/
│   ├── templates/cklab/
│   │   ├── base.html             # Base template (Bootstrap 5 + Kanit font)
│   │   ├── kiosk/                # User-facing templates
│   │   │   ├── index.html        # Check-in form
│   │   │   ├── timer.html        # Session timer
│   │   │   └── feedback.html     # Rating & feedback
│   │   └── admin/                # Admin-facing templates
│   │       ├── admin-login.html
│   │       ├── admin-monitor.html
│   │       └── admin-config.html
│   └── static/cklab/
│       ├── css/
│       │   ├── main.css          # Global styles
│       │   └── admin.css         # Admin sidebar
│       ├── js/
│       │   ├── auth.js
│       │   ├── admin-login.js
│       │   ├── timer.js          # Timer + API sync ทุก 5 วินาที
│       │   └── feedback.js       # Star rating interaction
│       └── img/
│           └── ubulogo.png
│
├── .env                          # Environment variables (ไม่เข้า git)
├── .env.example                  # Template สำหรับ .env
├── .gitignore
├── docker-compose.yml            # PostgreSQL 15 (อ่านค่าจาก .env)
├── manage.py
└── README.md
```

---

## 2. Tech Stack

| Layer | Technology |
|:---|:---|
| Backend | Python 3.10+ / Django 5.0 |
| Database | PostgreSQL 15 (Docker) |
| Frontend | Django Templates + Bootstrap 5.3 + Vanilla JS |
| Font | Google Fonts — Kanit (ภาษาไทย) |
| Package Manager | uv (Astral) |

---

## 3. Environment Variables

โปรเจกต์ใช้ไฟล์ `.env` เก็บค่า config ทั้งหมด (ไม่ hardcode ใน source code)

### ไฟล์ที่เกี่ยวข้อง

| ไฟล์ | หน้าที่ | เข้า Git? |
|:---|:---|:---|
| `.env` | ค่าจริงที่ใช้รัน (มี password/secret) | ไม่ (อยู่ใน `.gitignore`) |
| `.env.example` | Template ให้คนในทีม copy ไปสร้าง `.env` | ใช่ |

### ตัวแปรทั้งหมด

| Variable | ใช้ใน | ตัวอย่าง |
|:---|:---|:---|
| `SECRET_KEY` | `settings.py` | `django-insecure-setup-key` |
| `DEBUG` | `settings.py` | `True` / `False` |
| `ALLOWED_HOSTS` | `settings.py` | `localhost,127.0.0.1` |
| `POSTGRES_DB` | `settings.py`, `docker-compose.yml` | `cklab_db` |
| `POSTGRES_USER` | `settings.py`, `docker-compose.yml` | `cklab_admin` |
| `POSTGRES_PASSWORD` | `settings.py`, `docker-compose.yml` | `secretpassword` |
| `POSTGRES_HOST` | `settings.py` | `localhost` |
| `POSTGRES_PORT` | `settings.py` | `5432` |

### วิธีตั้งค่า (สำหรับสมาชิกใหม่)

```powershell
# copy template แล้วแก้ค่าตามต้องการ
cp .env.example .env
```

---

## 4. Quick Start

```powershell
# 1. ติดตั้ง dependencies
uv venv
.\.venv\Scripts\activate
uv pip install django psycopg2-binary python-dotenv

# 2. ตั้งค่า environment
cp .env.example .env          # แก้ค่าใน .env ตามต้องการ

# 3. รัน database
docker compose up -d

# 4. migrate & สร้าง superuser
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# 5. รัน server
python manage.py runserver
```

เปิดเบราว์เซอร์:
- **Kiosk (User):** `http://localhost:8000/`
- **Admin Login:** `http://localhost:8000/admin-portal/login/`
- **Django Admin:** `http://localhost:8000/django-admin/`

---

## 5. Database Models

### SiteConfig (Singleton — 1 row เท่านั้น) (ผู้รับผิดชอบ: ภานุวัฒน์)
| Field | Type | Note |
|:---|:---|:---|
| `lab_name` | CharField(100) | default `"CKLab"` — ชื่อห้องแลป |
| `max_session_minutes` | PositiveIntegerField | default `120` — เวลาจำกัด session (นาที) |
| `booking_enabled` | BooleanField | default `True` — เปิด/ปิดระบบจอง |
| `announcement` | TextField | default `""` — ข้อความประกาศ |

เรียกใช้: `SiteConfig.get()` → จะ get_or_create row pk=1 อัตโนมัติ

### Software (ผู้รับผิดชอบ: ลลิดา)
| Field | Type | Note |
|:---|:---|:---|
| `name` | CharField(100) | |
| `version` | CharField(50) | |
| `software_type` | CharField(20) | choices: `AI`, `Software` |

### Booking (ผู้รับผิดชอบ: อัษฎาวุธ)
| Field | Type | Note |
|:---|:---|:---|
| — | — | รอกำหนด field โดยผู้รับผิดชอบ |

### Status (ผู้รับผิดชอบ: ณัฐกรณ์)
| Field | Type | Note |
|:---|:---|:---|
| — | — | ใช้ระบุสถานะของเครื่องคอมพิวเตอร์ — รอกำหนด field โดยผู้รับผิดชอบ |

### Computer (ผู้รับผิดชอบ: ธนสิทธิ์)
| Field | Type | Note |
|:---|:---|:---|
| `pc_id` | CharField(10) | unique — เช่น `"1"`, `"2"` |
| `name` | CharField(50) | เช่น `"PC-1"` |
| `status` | CharField(20) | `available` / `in_use` / `reserved` / `maintenance` |
| `pc_type` | CharField(20) | default `"General"` |
| `installed_software` | ManyToMany → Software | |
| `current_user` | CharField(100) | nullable — ชื่อผู้ใช้ปัจจุบัน |
| `session_start` | DateTimeField | nullable — เวลาเริ่ม session |

### UsageLog (ผู้รับผิดชอบ: เขมมิกา)
| Field | Type | Note |
|:---|:---|:---|
| `user_id` | CharField(50) | |
| `user_name` | CharField(100) | |
| `computer` | FK → Computer | `on_delete=SET_NULL` |
| `start_time` | DateTimeField | |
| `end_time` | DateTimeField | `auto_now_add=True` |
| `satisfaction_score` | IntegerField | nullable — คะแนน 1-5 |

---

## 6. Views — Class-Based Views (CBV)

โปรเจกต์ใช้ CBV ทั้งหมด แยกไฟล์ตามผู้รับผิดชอบใน `lab_management/views/`

### 6.1 Kiosk Views (ไม่ต้อง Login) — ผู้รับผิดชอบ: ปภังกร

| Class | Base | HTTP Methods | หน้าที่ |
|:---|:---|:---|:---|
| `IndexView` | `View` | GET, POST | หน้า Check-in — GET แสดงฟอร์ม, POST บันทึก session |
| `ConfirmView` | `TemplateView` | GET | หน้ายืนยัน |
| `TimerView` | `View` | GET | แสดงเวลาใช้งาน (redirect ถ้าไม่มี session) |
| `FeedbackView` | `View` | GET, POST | GET แสดงฟอร์ม, POST บันทึก UsageLog + reset Computer |

### 6.2 Admin Views (ต้อง Login — `LoginRequiredMixin`)

| Class | Base | HTTP Methods | หน้าที่ | ผู้รับผิดชอบ |
|:---|:---|:---|:---|:---|
| `AdminMonitorView` | `LoginRequiredMixin, View` | GET, POST | Dashboard แสดง Computer ทั้งหมด | ธนสิทธิ์ |
| `AdminBookingView` | `LoginRequiredMixin, View` | GET, POST | จัดการการจอง | อัษฎาวุธ |
| `AdminImportBookingView` | `LoginRequiredMixin, View` | POST | Import ข้อมูล Booking | อัษฎาวุธ |
| `AdminManagePcView` | `LoginRequiredMixin, View` | GET, POST | จัดการ PC + สถานะ | ณัฐกรณ์ |
| `AdminSoftwareView` | `LoginRequiredMixin, View` | GET, POST | จัดการ Software | ลลิดา |
| `AdminReportView` | `LoginRequiredMixin, View` | GET | รายงาน | เขมมิกา |
| `AdminReportExportView` | `LoginRequiredMixin, View` | GET | Export UsageLog เป็น CSV | เขมมิกา |
| `AdminConfigView` | `LoginRequiredMixin, View` | GET, POST | ดู/แก้ไข SiteConfig | ภานุวัฒน์ |

### 6.3 API Views — ผู้รับผิดชอบ: ธนสิทธิ์

| Class | Base | Endpoint | Response |
|:---|:---|:---|:---|
| `ApiMonitorDataView` | `View` | `GET /api/monitor-data/` | `JsonResponse` — ข้อมูล Computer ทั้งหมด |

---

## 7. URL Routing

Root: `cklab_project/urls.py` → `include('lab_management.urls')`

```
/                              → IndexView          (Kiosk Check-in)
/confirm/                      → ConfirmView         (ยืนยัน)
/timer/                        → TimerView           (จับเวลา)
/feedback/                     → FeedbackView        (ให้คะแนน)

/admin-portal/login/           → Django LoginView
/admin-portal/logout/          → Django LogoutView

/admin-portal/monitor/         → AdminMonitorView
/admin-portal/booking/         → AdminBookingView
/admin-portal/manage-pc/       → AdminManagePcView
/admin-portal/software/        → AdminSoftwareView
/admin-portal/report/          → AdminReportView
/admin-portal/report/export/   → AdminReportExportView  (Export CSV)
/admin-portal/config/          → AdminConfigView

/api/monitor-data/             → ApiMonitorDataView

/django-admin/                 → Django Admin Site
```

---

## 8. Authentication Flow

```
settings.py:
  LOGIN_URL           = '/admin-portal/login/'
  LOGIN_REDIRECT_URL  = '/admin-portal/monitor/'
  LOGOUT_REDIRECT_URL = '/admin-portal/login/'
```

- Admin views ใช้ `LoginRequiredMixin` — ถ้ายังไม่ login จะ redirect ไป `LOGIN_URL`
- Login/Logout ใช้ Django built-in `auth_views.LoginView` / `LogoutView`
- Kiosk views ไม่ต้อง login (เปิดใช้งานได้เลย)

---

## 9. Session Flow (Kiosk)

```
IndexView (POST)
  → บันทึก Computer.status = 'in_use'
  → เก็บ session: session_pc_id, session_user_name, session_start_time
  → redirect → TimerView

TimerView (GET)
  → อ่าน session → แสดงเวลาใช้งาน
  → timer.js sync กับ /api/monitor-data/ ทุก 5 วินาที

FeedbackView (POST)
  → สร้าง UsageLog
  → reset Computer (status='available', current_user=None)
  → session.flush()
  → redirect → IndexView
```

---

## 10. แนวทางการเพิ่ม View ใหม่ (สำหรับสมาชิกในทีม)

> แต่ละคนแก้ไขเฉพาะไฟล์ `views/` ของตัวเองเท่านั้น

### ขั้นตอน

**1) เขียน logic** ในไฟล์ `views/` ของตัวเอง เช่น `views/booking.py`:

```python
# views/booking.py
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from ..models import Booking

class AdminBookingView(LoginRequiredMixin, View):
    def get(self, request):
        bookings = Booking.objects.all()
        return render(request, 'cklab/admin/admin-booking.html', {'bookings': bookings})

    def post(self, request):
        # บันทึกข้อมูล...
        return redirect('admin_booking')
```

**2) Export class** ใน `views/__init__.py` (ถ้าเพิ่ม class ใหม่):

```python
# views/__init__.py
from .booking import AdminBookingView, AdminImportBookingView  # เพิ่ม class ใหม่ตรงนี้
```

**3) เพิ่ม URL** ใน `lab_management/urls.py` (ถ้ามี route ใหม่):

```python
path('admin-portal/booking/', views.AdminBookingView.as_view(), name='admin_booking'),
```

**4) สร้าง Template** ใน `templates/cklab/admin/`:

```html
{% extends "cklab/base.html" %}
{% block title %}Booking{% endblock %}
{% block content %}
  <!-- เนื้อหา -->
{% endblock %}
```

**5) อัปเดต Model (ถ้าจำเป็น)** ใน `lab_management/models.py` แล้วรัน:

```powershell
python manage.py makemigrations
python manage.py migrate
```

---

## 11. CBV Cheat Sheet

| ต้องการ | ใช้ Base Class | ตัวอย่าง |
|:---|:---|:---|
| แค่ render template | `TemplateView` | `ConfirmView` |
| render + ส่ง context | `TemplateView` + override `get_context_data` | `AdminMonitorView` |
| GET + POST custom logic | `View` + define `get()` / `post()` | `IndexView`, `FeedbackView` |
| CRUD model | `ListView`, `CreateView`, `UpdateView`, `DeleteView` | (ยังไม่ได้ใช้) |
| ต้อง Login | เพิ่ม `LoginRequiredMixin` เป็น class แรก | `AdminMonitorView` |
| Return JSON | `View` + `JsonResponse` | `ApiMonitorDataView` |

---

## 12. Database (Docker)

```yaml
# docker-compose.yml — อ่านค่าจาก .env โดยอัตโนมัติ
services:
  db:
    image: postgres:15
    container_name: cklab_postgres
    env_file:
      - .env          # ใช้ POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    ports:
      - "5432:5432"
```

คำสั่งที่ใช้บ่อย:

```powershell
docker compose up -d          # เปิด database
docker compose down            # ปิด database
docker compose down -v         # ปิด + ลบข้อมูลทั้งหมด
docker ps                      # เช็คสถานะ container
```

---

## 13. Git Workflow

```powershell
# ดึงโค้ดล่าสุด
git pull origin main

# สร้าง branch ใหม่สำหรับ feature
git checkout -b feature/your-feature-name

# commit & push
git add .
git commit -m "Add your feature description"
git push origin feature/your-feature-name

# สร้าง Pull Request บน GitHub → merge เข้า main
```
