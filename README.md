# CKLab Management System

ระบบบริหารจัดการห้องปฏิบัติการคอมพิวเตอร์ (Check-in / Check-out / Booking / Monitor / Report)
พัฒนาด้วย **Django 5 + PostgreSQL 15** และรันระบบทั้งหมดผ่าน **Docker Compose**

---

## 📦 Tech Stack

| Layer          | Technology                                    |
| -------------- | --------------------------------------------- |
| Infrastructure | Docker & Docker Compose                       |
| Backend        | Python 3.10+ / Django 5.0                     |
| Database       | PostgreSQL 15                                 |
| Frontend       | Django Templates + Bootstrap 5.3 + Vanilla JS |
| Font           | Google Fonts — Kanit                          |

---

# 📁 Project Structure

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
│   ├── views/                    # Class-Based Views (CBV)
│   ├── forms/                    # Django Forms
│   ├── urls.py                   # URL patterns ทั้งหมด
│   ├── admin.py                  # Django admin registration
│   ├── management/commands/      # Custom commands (เช่น seed_data.py)
│   ├── templates/cklab/          # HTML Templates
│   └── static/cklab/             # CSS, JS, Images
│
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── README.md
```

---

# ⚙️ Environment Variables

โปรเจกต์ใช้ไฟล์ `.env` สำหรับเก็บค่าการตั้งค่า (ไม่ควร commit เข้า git)

### วิธีตั้งค่าสำหรับสมาชิกใหม่

```powershell
cp .env.example .env
```

---

# 🚀 Quick Start (Run with Docker)

> ไม่ต้องติดตั้ง Python หรือ PostgreSQL ลงเครื่อง

### 1️⃣ Setup ครั้งแรก

```powershell
# คัดลอก environment file
cp .env.example .env

# Build และรัน Web + Database
docker-compose up --build -d

# สร้างตารางในฐานข้อมูล
docker-compose exec web python manage.py migrate

# Seed ข้อมูลเริ่มต้น + Superuser
docker-compose exec web python manage.py seed_data
```

### 🔐 Default Admin

```
Username: admin
Password: admin1234
```

---

# 🌐 Access URLs

| ระบบ         | URL                                                                                    |
| ------------ | -------------------------------------------------------------------------------------- |
| Kiosk        | [http://localhost:8000/](http://localhost:8000/)                                       |
| Admin Portal | [http://localhost:8000/admin-portal/login/](http://localhost:8000/admin-portal/login/) |
| Django Admin | [http://localhost:8000/django-admin/](http://localhost:8000/django-admin/)             |

---

# 🐳 Docker Commands ที่ใช้บ่อย

```powershell
# รันระบบ
docker-compose up -d

# ปิดระบบ
docker-compose down

# ดู Log แบบ Real-time
docker-compose logs -f web

# เข้า Container
docker-compose exec web bash

# สั่งคำสั่ง Django โดยตรง
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

> ⚠️ ถ้ามีการเพิ่ม library ใหม่ใน requirements.txt ต้องรัน:

```
docker-compose up --build -d
```

---

# 🗄️ Database Models

| Model       | หน้าที่                   |
| ----------- | ------------------------- |
| SiteConfig  | เก็บค่า config ระบบ       |
| AdminonDuty | ข้อมูลเจ้าหน้าที่ประจำวัน |
| Software    | ข้อมูล Software/AI        |
| Booking     | ข้อมูลการจอง              |
| Computer    | ข้อมูลเครื่องคอมพิวเตอร์  |
| UsageLog    | บันทึกประวัติการใช้งาน    |

---

# 🧠 Views (Class-Based Views)

โปรเจกต์ใช้ **CBV ทั้งหมด**

## 🖥 Kiosk (ไม่ต้อง Login)

| URL                                | View         |
| ---------------------------------- | ------------ |
| `/`                                | IndexView    |
| `/checkin/<pc_id>/`                | CheckinView  |
| `/checkout/<pc_id>/`               | CheckoutView |
| `/status/<pc_id>/`                 | StatusView   |
| `/feedback/<pc_id>/<software_id>/` | FeedbackView |

---

## 🔐 Admin Portal (Login Required)

ใช้ `LoginRequiredMixin`

ตัวอย่าง:

```
/admin-portal/login/
/admin-portal/monitor/
/admin-portal/booking/
/admin-portal/report/
```

---

# 🔄 Session Flow

### Admin Session

* ใช้ `LoginRequiredMixin`
* Login สำเร็จ → อัปเดต AdminonDuty

### Kiosk Session

เก็บค่า:

* `pc_id`
* `user_name`
* `start_time`

เมื่อ Checkout หรือ Feedback เสร็จ:

```
session.flush()
```

---

# 🛠 Development Workflow

### ขั้นตอนทำ Feature ใหม่

1. เขียน logic ใน `views/`
2. Export class ใน `views/__init__.py`
3. เพิ่ม URL ใน `lab_management/urls.py`
4. สร้าง Template ใน `templates/cklab/admin/`
5. หากแก้ Model:

```powershell
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

---

# 🌿 Git Workflow

```powershell
# ดึงโค้ดล่าสุด
git pull origin main

# สร้าง branch ใหม่
git checkout -b feature/your-feature-name

# commit
git add .
git commit -m "Add your feature description"

# push
git push origin feature/your-feature-name
```

### Merge โค้ดเพื่อนเข้า Branch ตัวเอง

```powershell
git checkout main
git pull origin main

git checkout feature/your-feature-name
git merge main
```

---

# 🧩 Important Notes

* 🟢 แก้ไฟล์ Python → Docker Hot Reload อัตโนมัติ
* 🔴 เพิ่ม Library ใหม่ → ต้อง `--build`
* ❌ ห้าม commit `.env`
* ✅ ต้องสร้าง Pull Request ก่อน merge เข้า `main`

---

# 👨‍💻 สำหรับทีมพัฒนา

ระบบนี้ออกแบบให้:

* เริ่มต้นได้ภายใน 5 นาที
* ไม่ต้องติดตั้ง dependency ลงเครื่อง
* แยกความรับผิดชอบชัดเจน
* รองรับการพัฒนาแบบ Team Workflow
