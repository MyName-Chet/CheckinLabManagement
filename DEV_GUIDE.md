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
│   ├── models.py                 # SiteConfig, AdminonDuty, Software, Booking, Computer, UsageLog
│   ├── views/                    # Class-Based Views (CBV) — แยกไฟล์ตามผู้รับผิดชอบ
│   │   ├── __init__.py           # Re-export ทุก class (urls.py ใช้งานได้เหมือนเดิม)
│   │   ├── auth.py               # สถาพร: LoginView, LogoutView
│   │   ├── kiosk.py              # ปภังกร: IndexView, CheckinView, CheckoutView, StatusView, FeedbackView
│   │   ├── monitor.py            # ธนสิทธิ์: AdminMonitorView, AdminCheckinView, AdminCheckoutView
│   │   ├── booking.py            # อัษฎาวุธ: AdminBookingView, AdminBookingDetailView, AdminImportBookingView
│   │   ├── manage_pc.py          # ณัฐกรณ์: AdminManagePcView, AdminAddPcView, AdminManagePcEditView, AdminManagePcDeleteView
│   │   ├── software.py           # ลลิดา: AdminSoftwareView, AdminSoftwareEditView, AdminSoftwareDeleteView
│   │   ├── report.py             # เขมมิกา: AdminReportView, AdminReportExportView
│   │   └── config.py             # ภานุวัฒน์: AdminConfigView, AdminUserView, AdminUserEditView, AdminUserDeleteView
│   ├── forms/                    # Django Forms — แยกไฟล์ตามผู้รับผิดชอบ
│   │   ├── __init__.py           # Re-export ทุก form class
│   │   ├── kiosk.py              # ปภังกร: CheckinForm, FeedbackForm
│   │   ├── booking.py            # อัษฎาวุธ: BookingForm, ImportBookingForm
│   │   ├── manage_pc.py          # ณัฐกรณ์: PcForm
│   │   ├── software.py           # ลลิดา: SoftwareForm
│   │   ├── report.py             # เขมมิกา: ReportFilterForm
│   │   └── config.py             # ภานุวัฒน์: SiteConfigForm, AdminUserForm, AdminUserEditForm
│   ├── urls.py                   # URL patterns ทั้งหมด
│   ├── admin.py                  # Django admin registration
│   ├── apps.py
│   ├── tests.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py      # `python manage.py seed_data` — สร้างข้อมูลเริ่มต้น (Software, Computer, UsageLog, Booking, superuser)
│   ├── migrations/
│   ├── templates/cklab/
│   │   ├── base.html             # Base template (Bootstrap 5 + Kanit font)
│   │   ├── kiosk/                # User-facing templates
│   │   │   ├── index.html        # Check-in form
│   │   │   ├── checkin.html      # Checkin page
│   │   │   ├── checkout.html     # Checkout page
│   │   │   ├── status.html       # Session status
│   │   │   └── feedback.html     # Rating & feedback
│   │   └── admin/                # Admin-facing templates
│   │       ├── admin-login.html
│   │       ├── admin-monitor.html
│   │       ├── admin-booking.html
│   │       ├── admin-booking-import.html
│   │       ├── admin-manage-pc.html
│   │       ├── admin-software.html
│   │       ├── admin-software-edit.html
│   │       ├── admin-report.html
│   │       ├── admin-users.html
│   │       ├── admin-users-edit.html
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

### 4.1 ติดตั้งและเริ่มต้น

```powershell
# 1. ติดตั้ง dependencies
uv venv
.\.venv\Scripts\activate
uv pip install django psycopg2-binary python-dotenv

# 2. ตั้งค่า environment
cp .env.example .env          # แก้ค่าใน .env ตามต้องการ

# 3. รัน database (PostgreSQL via Docker)
docker compose up -d

# 4. สร้าง migration จาก models.py แล้ว apply เข้า database
python manage.py makemigrations
python manage.py migrate

# 5. seed ข้อมูลตัวอย่าง (Software, Computer, UsageLog, Booking + superuser)
python manage.py seed_data    # admin / admin1234

# 6. รัน server
python manage.py runserver
```

เปิดเบราว์เซอร์:
- **Kiosk (User):** `http://localhost:8000/`
- **Admin Login:** `http://localhost:8000/admin-portal/login/`
- **Django Admin:** `http://localhost:8000/django-admin/`

---

### 4.2 แนวทางการเริ่มต้นพัฒนา (สำหรับนักศึกษา)

> **เป้าหมาย:** เติม logic ใน `views/` ของตัวเองให้ครบ แต่ละ method ปัจจุบันมีแค่ `pass`

#### ขั้นตอนที่แนะนำ

**ขั้นที่ 1 — ทำความเข้าใจ Model ที่ต้องใช้**

เปิดไฟล์ `views/` ของตัวเอง อ่าน comment `# TODO: Models ที่ต้องใช้` แล้วเปิด `models.py` ดู field ที่มี

```python
# ตัวอย่าง: ถ้าต้องการดึงรายการ Computer ทั้งหมด
from ..models import Computer
computers = Computer.objects.all()
```

**ขั้นที่ 2 — เพิ่ม import ที่จำเป็น**

ไฟล์แต่ละไฟล์มี comment บอกไว้แล้วว่าต้องใช้อะไร:

```python
# ตัวอย่าง imports ที่ใช้บ่อย
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from ..models import Computer, Software   # เปลี่ยนตาม TODO ในไฟล์ตัวเอง
```

**ขั้นที่ 3 — เขียน GET: ดึงข้อมูลแล้ว render template**

```python
def get(self, request):
    computers = Computer.objects.all()
    return render(request, 'cklab/admin/admin-monitor.html', {'computers': computers})
```

**ขั้นที่ 4 — เขียน POST: รับข้อมูลจาก Form แล้วบันทึก**

```python
def post(self, request):
    # รับค่าจาก form
    pc_id = request.POST.get('pc_id')
    # บันทึก / อัปเดต database
    Computer.objects.filter(pk=pc_id).update(status='IN_USE')
    return redirect('admin_monitor')
```

**ขั้นที่ 5 — ถ้า model มีการเปลี่ยนแปลง ให้รัน migration ใหม่**

```powershell
python manage.py makemigrations
python manage.py migrate
```

**ขั้นที่ 6 — รัน tests เพื่อตรวจสอบว่าไม่ได้ทำให้อะไรพัง**

```powershell
DJANGO_SETTINGS_MODULE=cklab_project.settings_test python manage.py test lab_management
```

---

## 5. Database Models

| Model | ผู้รับผิดชอบ | หน้าที่ |
|:---|:---|:---|
| `SiteConfig` | ภานุวัฒน์ | เก็บค่า config ของระบบ |
| `AdminonDuty` | ภานุวัฒน์ | ข้อมูลเจ้าหน้าที่ดูแลระบบประจำวัน |
| `Software` | ลลิดา | ข้อมูล Software/AI ที่ติดตั้งในห้อง |
| `Booking` | อัษฎาวุธ | ข้อมูลการจองเครื่องคอมพิวเตอร์ |
| `Computer` | ณัฐกรณ์ + ธนสิทธิ์ | ข้อมูลและสถานะเครื่องคอมพิวเตอร์แต่ละเครื่อง |
| `UsageLog` | เขมมิกา | บันทึกประวัติการใช้งานคอมพิวเตอร์ |

> **หมายเหตุ:** `Status` model ถูกยุบรวมเข้า `Computer` แล้ว (field `status` อยู่ใน `Computer` โดยตรง)

---

### SiteConfig (ผู้รับผิดชอบ: ภานุวัฒน์)

| Field | Type | Note |
|:---|:---|:---|
| `lab_name` | `CharField` | ชื่อห้องปฏิบัติการ (default: "CKLab") |
| `booking_enabled` | `BooleanField` | เปิด/ปิด ระบบจอง |
| `announcement` | `TextField` | ข้อความประกาศบนหน้า Kiosk |
| `location` | `CharField` | สถานที่ตั้ง |
| `is_open` | `BooleanField` | สถานะเปิด/ปิดห้องแล็บ |
| `admin_on_duty` | `ForeignKey → AdminonDuty` | เจ้าหน้าที่ดูแลประจำวัน |

### AdminonDuty (ผู้รับผิดชอบ: ภานุวัฒน์)

| Field | Type | Note |
|:---|:---|:---|
| `admin_on_duty` | `CharField` | ชื่อเจ้าหน้าที่ดูแลระบบ |
| `contact_phone` | `CharField` | เบอร์โทรศัพท์ติดต่อ |
| `contact_email` | `EmailField` | อีเมลติดต่อ |

### Software (ผู้รับผิดชอบ: ลลิดา)

| Field | Type | Note |
|:---|:---|:---|
| `name` | `CharField` | ชื่อรายการ |
| `version` | `CharField` | แพ็กเกจ / เวอร์ชัน |
| `type` | `CharField` | ประเภท: `"Software"` หรือ `"AI"` |
| `expire_date` | `DateField` | วันหมดอายุ License (nullable) |

### Booking (ผู้รับผิดชอบ: อัษฎาวุธ)

| Field | Type | Note |
|:---|:---|:---|
| `student_id` | `CharField` | รหัสนักศึกษา/ผู้ใช้ |
| `computer` | `ForeignKey → Computer` | เครื่องที่จอง (nullable) |
| `start_time` | `DateTimeField` | เวลาเริ่มใช้งาน |
| `end_time` | `DateTimeField` | เวลาสิ้นสุดการใช้งาน |
| `booking_date` | `DateTimeField` | วันที่ทำการจอง |
| `status` | `CharField` | `APPROVED` (การจองทุกรายการจะถูกอนุมัติแล้ว ไม่มี PENDING/REJECTED) |
| `created_at` | `DateTimeField` | เวลาที่ทำรายการ |

### Computer (ผู้รับผิดชอบ: ณัฐกรณ์ + ธนสิทธิ์)

| Field | Type | Note |
|:---|:---|:---|
| `name` | `CharField` | ชื่อเครื่อง (unique) เช่น "PC-01" |
| `Software` | `ForeignKey → Software` | ซอฟต์แวร์ที่ติดตั้ง (1 เครื่อง = 1 software) |
| `status` | `CharField` | `AVAILABLE` / `IN_USE` / `RESERVED` / `MAINTENANCE` |
| `last_updated` | `DateTimeField` | อัปเดตสถานะล่าสุด (auto) |
| `description` | `TextField` | รายละเอียดเพิ่มเติม (nullable) |

### UsageLog (ผู้รับผิดชอบ: เขมมิกา)

| Field | Type | Note |
|:---|:---|:---|
| `user_id` | `CharField` | รหัสนักศึกษา/บุคลากร |
| `user_name` | `CharField` | ชื่อ-นามสกุล |
| `user_type` | `CharField` | `student` / `staff` / `guest` |
| `department` | `CharField` | คณะ/หน่วยงาน (nullable) |
| `user_year` | `CharField` | ชั้นปี (nullable) |
| `computer` | `CharField` | ชื่อเครื่องที่ใช้ (snapshot, ไม่ใช่ FK) |
| `Software` | `CharField` | ชื่อซอฟต์แวร์ที่ใช้ (snapshot, ไม่ใช่ FK) |
| `start_time` | `DateTimeField` | เวลา Check-in (auto) |
| `end_time` | `DateTimeField` | เวลา Check-out (nullable) |
| `satisfaction_score` | `IntegerField` | คะแนนความพึงพอใจ 1-5 (nullable) |
| `comment` | `TextField` | ข้อเสนอแนะเพิ่มเติม (nullable) |

---

## 6. Views — Class-Based Views (CBV)

โปรเจกต์ใช้ CBV ทั้งหมด แยกไฟล์ตามผู้รับผิดชอบใน `lab_management/views/`

### 6.1 Kiosk Views (ไม่ต้อง Login) — ผู้รับผิดชอบ: ปภังกร

| Class | Base | HTTP Methods | URL Parameter | หน้าที่ |
|:---|:---|:---|:---|:---|
| `IndexView` | `View` | GET, POST | — | หน้าหลัก Kiosk |
| `CheckinView` | `View` | GET, POST | `pc_id` | Check-in เข้าใช้เครื่อง |
| `CheckoutView` | `View` | GET, POST | `pc_id` | Check-out ออกจากเครื่อง |
| `StatusView` | `View` | GET | `pc_id` | ตรวจสอบ session ปัจจุบัน |
| `FeedbackView` | `View` | GET, POST | `pc_id`, `software_id` | ให้คะแนน Software หลัง Check-out |

### 6.2 Admin Views (ต้อง Login — `LoginRequiredMixin`)

| Class | Base | HTTP Methods | URL Parameter | หน้าที่ | ผู้รับผิดชอบ |
|:---|:---|:---|:---|:---|:---|
| `AdminUserView` | `LoginRequiredMixin, View` | GET, POST | — | ดูรายการ / เพิ่ม Admin User | สถาพร |
| `AdminUserEditView` | `LoginRequiredMixin, View` | GET, POST | `pk` | แก้ไข Admin User | สถาพร |
| `AdminUserDeleteView` | `LoginRequiredMixin, View` | POST | `pk` | ลบ Admin User | สถาพร |
| `AdminMonitorView` | `LoginRequiredMixin, View` | GET, POST | — | Dashboard แสดง Computer ทั้งหมด | ธนสิทธิ์ |
| `AdminCheckinView` | `LoginRequiredMixin, View` | POST | `pc_id` | Admin Check-in แทน User | ธนสิทธิ์ |
| `AdminCheckoutView` | `LoginRequiredMixin, View` | POST | `pc_id` | Admin Check-out แทน User | ธนสิทธิ์ |
| `AdminBookingView` | `LoginRequiredMixin, View` | GET, POST | — | ดูรายการ / เพิ่ม Booking | อัษฎาวุธ |
| `AdminBookingDetailView` | `LoginRequiredMixin, View` | GET, POST | `pk` | ดู / แก้ไข Booking รายการ | อัษฎาวุธ |
| `AdminImportBookingView` | `LoginRequiredMixin, View` | POST | — | Import ข้อมูล Booking จาก CSV | อัษฎาวุธ |
| `AdminManagePcView` | `LoginRequiredMixin, View` | GET | — | ดูรายการ PC ทั้งหมด | ณัฐกรณ์ |
| `AdminAddPcView` | `LoginRequiredMixin, View` | GET, POST | — | เพิ่ม PC ใหม่ | ณัฐกรณ์ |
| `AdminManagePcEditView` | `LoginRequiredMixin, View` | GET, POST | `pc_id` | แก้ไขข้อมูล PC | ณัฐกรณ์ |
| `AdminManagePcDeleteView` | `LoginRequiredMixin, View` | POST | `pc_id` | ลบ PC | ณัฐกรณ์ |
| `AdminSoftwareView` | `LoginRequiredMixin, View` | GET, POST | — | ดูรายการ / เพิ่ม Software | ลลิดา |
| `AdminSoftwareEditView` | `LoginRequiredMixin, View` | GET, POST | `pk` | แก้ไข Software | ลลิดา |
| `AdminSoftwareDeleteView` | `LoginRequiredMixin, View` | POST | `pk` | ลบ Software | ลลิดา |
| `AdminReportView` | `LoginRequiredMixin, View` | GET, POST | — | รายงานการใช้งาน | เขมมิกา |
| `AdminReportExportView` | `LoginRequiredMixin, View` | GET | — | Export UsageLog เป็น CSV | เขมมิกา |
| `AdminConfigView` | `LoginRequiredMixin, View` | GET, POST | — | ดู/แก้ไข SiteConfig | ภานุวัฒน์ |

---

## 7. URL Routing

Root: `cklab_project/urls.py` → `include('lab_management.urls')`

```
# Kiosk (ไม่ต้อง Login)
/                                          → IndexView
/checkin/<pc_id>/                          → CheckinView
/checkout/<pc_id>/                         → CheckoutView
/status/<pc_id>/                           → StatusView
/feedback/<pc_id>/<software_id>/           → FeedbackView

# Auth
/admin-portal/login/                       → Django LoginView
/admin-portal/logout/                      → Django LogoutView

# Admin User Management
/admin-portal/users/                       → AdminUserView
/admin-portal/users/<pk>/edit/             → AdminUserEditView
/admin-portal/users/<pk>/delete/           → AdminUserDeleteView

# Admin Monitor
/admin-portal/monitor/                     → AdminMonitorView
/admin-portal/checkin/<pc_id>/             → AdminCheckinView   (Admin checkin แทน user)
/admin-portal/checkout/<pc_id>/            → AdminCheckoutView  (Admin checkout แทน user)

# Booking
/admin-portal/booking/                     → AdminBookingView
/admin-portal/booking/<pk>/                → AdminBookingDetailView
/admin-portal/booking/import/              → AdminImportBookingView

# Manage PC
/admin-portal/manage-pc/                   → AdminManagePcView
/admin-portal/manage-pc/add/               → AdminAddPcView
/admin-portal/manage-pc/<pc_id>/edit/      → AdminManagePcEditView
/admin-portal/manage-pc/<pc_id>/delete/    → AdminManagePcDeleteView

# Software
/admin-portal/software/                    → AdminSoftwareView
/admin-portal/software/<pk>/edit/          → AdminSoftwareEditView
/admin-portal/software/<pk>/delete/        → AdminSoftwareDeleteView

# Report
/admin-portal/report/                      → AdminReportView
/admin-portal/report/export/               → AdminReportExportView

# Config
/admin-portal/config/                      → AdminConfigView

/django-admin/                             → Django Admin Site
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
- Login/Logout ใช้ custom `LoginView` / `LogoutView` ใน `views/auth.py` (extends Django built-in)
- Kiosk views ไม่ต้อง login (เปิดใช้งานได้เลย)

---

## 8.1 Admin Session Flow (Login → ใช้งาน → Logout)

```
LoginView (POST) — /admin-portal/login/
  → authenticate username / password
  → ถ้าสำเร็จ → บันทึก AdminonDuty:
      AdminonDuty.admin_on_duty  = request.user.get_full_name()
      AdminonDuty.contact_phone  = (ค่าที่กรอกใน login form หรือดึงจาก profile)
      AdminonDuty.contact_email  = request.user.email
  → SiteConfig.admin_on_duty = AdminonDuty ที่เพิ่งอัปเดต
  → redirect → AdminMonitorView

  [ระหว่างใช้งาน Admin Portal]
  → AdminConfigView (GET/POST) — /admin-portal/config/
      → แก้ไข SiteConfig (lab_name, is_open, announcement ฯลฯ)
      → แก้ไข AdminonDuty (ชื่อผู้ดูแล, เบอร์โทร, อีเมล)

LogoutView (POST) — /admin-portal/logout/
  → ล้างข้อมูล AdminonDuty ที่ผูกกับ SiteConfig:
      AdminonDuty.admin_on_duty  = None
      AdminonDuty.contact_phone  = None
      AdminonDuty.contact_email  = None
  → Django logout (session.flush())
  → redirect → LoginView
```

> **หมายเหตุ implementation (views/auth.py):**
> - `LoginView` — override `form_valid()` เพื่อ update `AdminonDuty` หลัง super() ผ่าน
> - `LogoutView` — override `dispatch()` เพื่อ clear `AdminonDuty` ก่อน super() logout

---

## 9. Session Flow (Kiosk)

```
IndexView (GET)
  → แสดงหน้าหลัก Kiosk

CheckinView (POST) — /checkin/<pc_id>/
  → รับ student_id / ชื่อผู้ใช้
  → บันทึก Computer.status = 'IN_USE'
  → ค้นหา Booking APPROVED ถัดไปของ PC นี้ (start_time >= now)
  → เก็บ session:
      session["pc_id"]            = pc_id
      session["user_name"]        = user_name
      session["start_time"]       = now.isoformat()
      session["next_booking_end"] = booking.end_time.isoformat()  # หรือ None
  → redirect → StatusView/<pc_id>/

StatusView (GET) — /status/<pc_id>/
  → อ่าน session → ส่ง next_booking_end ไปยัง template
  → template ฝัง djangoData = { startTime, nextBookingEnd } ให้ timer.js

  [timer.js — client side]
  → นับ elapsed time ขึ้น (Usage Time)
  → ถ้ามี nextBookingEnd:
      → คำนวณ remainingMs = nextBookingEnd - now
      → ถ้า remainingMs <= 15 นาที แสดง alertBox แจ้งเตือน
      → ถ้า remainingMs <= 5 นาที แสดง alertBox พร้อมนับถอยหลัง
      → ถ้า remainingMs <= 0 → แสดง modal บังคับ "กรุณาลุกจากที่นั่ง"

CheckoutView (POST) — /checkout/<pc_id>/
  → ยืนยัน Check-out
  → redirect → FeedbackView/<pc_id>/<software_id>/

FeedbackView (POST) — /feedback/<pc_id>/<software_id>/
  → สร้าง UsageLog
  → reset Computer (status='AVAILABLE')
  → session.flush()
  → redirect → IndexView
```

### Session keys ที่ใช้

| Key | ค่า | หมายเหตุ |
|:----|:----|:---------|
| `pc_id` | `int` | PK ของ Computer |
| `user_name` | `str` | ชื่อผู้ใช้ |
| `start_time` | ISO string | เวลา Check-in |
| `next_booking_end` | ISO string / `None` | เวลาสิ้นสุดของ Booking ถัดไป ใช้โดย timer.js เพื่อแจ้งเตือน |

---

## 10. Booking Flow (ผู้รับผิดชอบ: อัษฎาวุธ)

```
AdminBookingView (GET) — /admin-portal/booking/
  → แสดงรายการ Booking ทั้งหมด (filter ตาม date ถ้ามี)

AdminBookingView (POST) — /admin-portal/booking/
  → รับ BookingForm (student_id, computer, start_time, end_time)
  → บันทึก Booking → Computer.status = 'RESERVED'
  → redirect → AdminBookingView (GET)

AdminBookingDetailView (GET/POST) — /admin-portal/booking/<pk>/
  → GET: แสดงข้อมูล Booking
  → POST (edit): บันทึกการเปลี่ยนแปลง
  → POST (delete): ลบ Booking → Computer.status = 'AVAILABLE'
  → redirect → AdminBookingView (GET)

AdminImportBookingView (POST) — /admin-portal/booking/import/
  → รับไฟล์ .csv → อ่านทีละแถว → สร้าง Booking + ตั้ง Computer.status = 'RESERVED'
  → redirect → AdminBookingView (GET)
```

---

## 11. Forms (ภาพรวม)

โปรเจกต์ใช้ Django Forms แยกไฟล์ตามผู้รับผิดชอบใน `lab_management/forms/`

### Form Classes

| Form Class | ไฟล์ | ผู้รับผิดชอบ | ใช้กับ View |
|:---|:---|:---|:---|
| `CheckinForm` | `forms/kiosk.py` | ปภังกร | `CheckinView` |
| `FeedbackForm` | `forms/kiosk.py` | ปภังกร | `FeedbackView` |
| `BookingForm` | `forms/booking.py` | อัษฎาวุธ | `AdminBookingView`, `AdminBookingDetailView` |
| `ImportBookingForm` | `forms/booking.py` | อัษฎาวุธ | `AdminImportBookingView` |
| `PcForm` | `forms/manage_pc.py` | ณัฐกรณ์ | `AdminAddPcView`, `AdminManagePcEditView` |
| `SoftwareForm` | `forms/software.py` | ลลิดา | `AdminSoftwareView`, `AdminSoftwareEditView` |
| `ReportFilterForm` | `forms/report.py` | เขมมิกา | `AdminReportView` |
| `SiteConfigForm` | `forms/config.py` | ภานุวัฒน์ | `AdminConfigView` |
| `AdminUserForm` | `forms/config.py` | ภานุวัฒน์ | `AdminUserView` |
| `AdminUserEditForm` | `forms/config.py` | ภานุวัฒน์ | `AdminUserEditView` |

### วิธีใช้ Form ใน View

```python
# views/booking.py
from ..forms import BookingForm

class AdminBookingView(LoginRequiredMixin, View):
    def get(self, request):
        form = BookingForm()
        return render(request, 'cklab/admin/admin-booking.html', {'form': form})

    def post(self, request):
        form = BookingForm(request.POST)
        if form.is_valid():
            # บันทึกข้อมูล...
            return redirect('admin_booking')
        return render(request, 'cklab/admin/admin-booking.html', {'form': form})
```

### วิธีแสดง Form ใน Template

```html
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">บันทึก</button>
</form>
```

---

## 12. แนวทางการพัฒนา (สำหรับสมาชิกในทีม)

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

## 13. CBV Cheat Sheet

| ต้องการ | ใช้ Base Class | ตัวอย่าง |
|:---|:---|:---|
| render template เปล่า | `TemplateView` | — |
| render + ส่ง context | `View` + `render()` | `AdminMonitorView` |
| GET + POST custom logic | `View` + define `get()` / `post()` | `CheckinView`, `FeedbackView` |
| CRUD model | `ListView`, `CreateView`, `UpdateView`, `DeleteView` | (ยังไม่ได้ใช้) |
| ต้อง Login | เพิ่ม `LoginRequiredMixin` เป็น class แรก | `AdminMonitorView` |
| Return JSON | `View` + `JsonResponse` | — |

---

## 14. Database (Docker)

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15
    container_name: cklab_postgres
    restart: always
    env_file:
      - .env          # ใช้ POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

คำสั่งที่ใช้บ่อย:

```powershell
docker compose up -d          # เปิด database
docker compose down            # ปิด database
docker compose down -v         # ปิด + ลบข้อมูลทั้งหมด
docker ps                      # เช็คสถานะ container
```

---

## 15. Git Workflow

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

### Merge branch เข้า main (local)

```powershell
# สลับไป main
git checkout main

# ดึงโค้ดล่าสุดจาก remote ก่อนเสมอ
git pull origin main

# merge branch ของตัวเองเข้า main
git merge feature/your-feature-name

# push ขึ้น remote
git push origin main
```

### แก้ Merge Conflict

```powershell
# หลังจาก merge แล้วมี conflict — เปิดไฟล์ที่ conflict แก้ไขด้วยมือ จากนั้น:
git add .
git commit -m "Resolve merge conflict"

# ถ้าต้องการยกเลิก merge (กลับสู่สถานะก่อน merge)
git merge --abort
```

### ลบ branch หลัง merge เสร็จ

```powershell
# ลบ branch local
git branch -d feature/your-feature-name

# ลบ branch remote
git push origin --delete feature/your-feature-name
```
