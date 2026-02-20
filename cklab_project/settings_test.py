# settings_test.py — ใช้ PostgreSQL เหมือน production แต่สร้าง test database แยก
# รัน: DJANGO_SETTINGS_MODULE=cklab_project.settings_test python manage.py test lab_management
from .settings import *  # noqa: F401, F403

# Django จะสร้าง database ชื่อ test_<POSTGRES_DB> โดยอัตโนมัติและลบทิ้งหลัง test เสร็จ
# ไม่ต้องแก้ไข DATABASES — ใช้ค่าจาก settings.py (อ่านจาก .env) ได้เลย
