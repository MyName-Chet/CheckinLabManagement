"""
Tests — CKLab Management System
รัน: DJANGO_SETTINGS_MODULE=cklab_project.settings_test python manage.py test lab_management

หมายเหตุ: Views ยังอยู่ในขั้นตอนการพัฒนา (plain class, ยังไม่ extends View)
ดังนั้น tests ในชุดนี้ครอบคลุม:
  1. Model Tests    — ตรวจสอบ field, default, relation, constraint ของทุก Model
  2. URL Path Tests — ตรวจสอบว่า reverse() ให้ path ที่ถูกต้อง (ไม่ได้เรียก view จริง)
  3. Login Tests    — ตรวจสอบ LoginView / LogoutView (Django built-in — พร้อมใช้แล้ว)
"""
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AdminonDuty, Booking, Computer, SiteConfig, Software, UsageLog


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def make_software(**kwargs):
    defaults = {"name": "TestSW", "version": "1.0", "type": "Software", "expire_date": date(2026, 12, 31)}
    defaults.update(kwargs)
    return Software.objects.create(**defaults)


def make_computer(software=None, status="AVAILABLE", **kwargs):
    if software is None:
        software = make_software(name=f"SW-{Computer.objects.count()}")
    defaults = {"name": f"PC-{Computer.objects.count()+1:02d}", "Software": software, "status": status}
    defaults.update(kwargs)
    return Computer.objects.create(**defaults)


# ══════════════════════════════════════════════════════════════════════════════
# 1. Model Tests
# ══════════════════════════════════════════════════════════════════════════════

class SoftwareModelTest(TestCase):
    def test_create_software(self):
        sw = make_software(name="ChatGPT", version="Plus", type="AI")
        self.assertEqual(sw.name, "ChatGPT")
        self.assertEqual(sw.version, "Plus")
        self.assertEqual(sw.type, "AI")

    def test_str(self):
        sw = make_software(name="Claude", version="Pro")
        self.assertEqual(str(sw), "Claude (Pro)")

    def test_default_type_is_software(self):
        sw = Software.objects.create(name="Canva", version="Free")
        self.assertEqual(sw.type, "Software")

    def test_expire_date_nullable(self):
        sw = Software.objects.create(name="NoExpire", version="1.0")
        self.assertIsNone(sw.expire_date)

    def test_type_choices(self):
        valid_types = [c[0] for c in Software.TYPE_CHOICES]
        self.assertIn("Software", valid_types)
        self.assertIn("AI", valid_types)


class ComputerModelTest(TestCase):
    def setUp(self):
        self.sw = make_software()

    def test_create_computer(self):
        pc = Computer.objects.create(name="PC-01", Software=self.sw, status="AVAILABLE")
        self.assertEqual(pc.name, "PC-01")
        self.assertEqual(pc.status, "AVAILABLE")

    def test_default_status_is_available(self):
        pc = Computer.objects.create(name="PC-02", Software=self.sw)
        self.assertEqual(pc.status, "AVAILABLE")

    def test_name_unique(self):
        Computer.objects.create(name="PC-DUP", Software=self.sw)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Computer.objects.create(name="PC-DUP", Software=self.sw)

    def test_status_choices(self):
        valid = [c[0] for c in Computer.STATUS_CHOICES]
        self.assertIn("AVAILABLE", valid)
        self.assertIn("IN_USE", valid)
        self.assertIn("RESERVED", valid)
        self.assertIn("MAINTENANCE", valid)

    def test_last_updated_auto(self):
        pc = Computer.objects.create(name="PC-03", Software=self.sw)
        self.assertIsNotNone(pc.last_updated)

    def test_software_fk_set_null_on_delete(self):
        sw = make_software(name="ToDelete")
        pc = Computer.objects.create(name="PC-04", Software=sw)
        sw.delete()
        pc.refresh_from_db()
        self.assertIsNone(pc.Software)

    def test_description_nullable(self):
        pc = Computer.objects.create(name="PC-05", Software=self.sw)
        self.assertIsNone(pc.description)


class AdminonDutyModelTest(TestCase):
    def test_create(self):
        duty = AdminonDuty.objects.create(
            admin_on_duty="อาจารย์ A",
            contact_phone="081-000-0000",
            contact_email="a@test.com",
        )
        self.assertEqual(duty.admin_on_duty, "อาจารย์ A")

    def test_all_fields_nullable(self):
        duty = AdminonDuty.objects.create()
        self.assertIsNone(duty.admin_on_duty)
        self.assertIsNone(duty.contact_phone)
        self.assertIsNone(duty.contact_email)


class SiteConfigModelTest(TestCase):
    def test_create_with_defaults(self):
        config = SiteConfig.objects.create()
        self.assertEqual(config.lab_name, "CKLab")
        self.assertTrue(config.booking_enabled)
        self.assertTrue(config.is_open)

    def test_admin_on_duty_fk(self):
        duty = AdminonDuty.objects.create(admin_on_duty="B")
        config = SiteConfig.objects.create(admin_on_duty=duty)
        self.assertEqual(config.admin_on_duty, duty)

    def test_admin_on_duty_set_null_on_delete(self):
        duty = AdminonDuty.objects.create(admin_on_duty="C")
        config = SiteConfig.objects.create(admin_on_duty=duty)
        duty.delete()
        config.refresh_from_db()
        self.assertIsNone(config.admin_on_duty)


class BookingModelTest(TestCase):
    def setUp(self):
        self.pc = make_computer()
        self.now = timezone.now()

    def test_create_booking(self):
        booking = Booking.objects.create(
            student_id="65010001",
            computer=self.pc,
            start_time=self.now,
            end_time=self.now + timedelta(hours=2),
            status="APPROVED",
        )
        self.assertEqual(booking.student_id, "65010001")
        self.assertEqual(booking.status, "APPROVED")

    def test_default_status_is_pending(self):
        # field ยังมีอยู่ใน model; ในทางปฏิบัติจะ set APPROVED เสมอ
        booking = Booking.objects.create(
            student_id="65010002",
            computer=self.pc,
            start_time=self.now,
            end_time=self.now + timedelta(hours=1),
        )
        self.assertEqual(booking.status, "PENDING")

    def test_computer_nullable(self):
        booking = Booking.objects.create(
            student_id="65010003",
            start_time=self.now,
            end_time=self.now + timedelta(hours=1),
        )
        self.assertIsNone(booking.computer)

    def test_booking_date_auto(self):
        booking = Booking.objects.create(
            student_id="65010004",
            computer=self.pc,
            start_time=self.now,
            end_time=self.now + timedelta(hours=1),
        )
        self.assertIsNotNone(booking.booking_date)

    def test_computer_set_null_on_delete(self):
        pc2 = make_computer()
        booking = Booking.objects.create(
            student_id="65010005",
            computer=pc2,
            start_time=self.now,
            end_time=self.now + timedelta(hours=1),
        )
        pc2.delete()
        booking.refresh_from_db()
        self.assertIsNone(booking.computer)


class UsageLogModelTest(TestCase):
    def test_create_usage_log(self):
        log = UsageLog.objects.create(
            user_id="65010001",
            user_name="สมชาย ใจดี",
            user_type="student",
            department="วิทยาศาสตร์",
            computer="PC-01",
            Software="ChatGPT",
        )
        self.assertEqual(log.user_id, "65010001")
        self.assertEqual(log.user_type, "student")

    def test_start_time_auto_now_add(self):
        log = UsageLog.objects.create(user_id="X", user_name="Y")
        self.assertIsNotNone(log.start_time)

    def test_end_time_nullable(self):
        log = UsageLog.objects.create(user_id="X2", user_name="Y2")
        self.assertIsNone(log.end_time)

    def test_satisfaction_score_nullable(self):
        log = UsageLog.objects.create(user_id="X3", user_name="Y3")
        self.assertIsNone(log.satisfaction_score)

    def test_user_type_choices(self):
        for utype in ("student", "staff", "guest"):
            log = UsageLog.objects.create(user_id="X4", user_name="Y4", user_type=utype)
            self.assertEqual(log.user_type, utype)

    def test_computer_is_charfield_snapshot(self):
        # UsageLog.computer เป็น CharField (snapshot) ไม่ใช่ FK
        log = UsageLog.objects.create(user_id="X5", user_name="Y5", computer="PC-99")
        self.assertEqual(log.computer, "PC-99")


# ══════════════════════════════════════════════════════════════════════════════
# 2. URL Path Tests — ตรวจสอบ reverse() ให้ path ที่ถูกต้อง
#    (ไม่ได้เรียก view จริง เพราะ views ยังอยู่ระหว่างพัฒนา)
# ══════════════════════════════════════════════════════════════════════════════

class KioskUrlTest(TestCase):
    def test_index_url(self):
        self.assertEqual(reverse("index"), "/")

    def test_checkin_url(self):
        self.assertEqual(reverse("checkin", kwargs={"pc_id": "PC-01"}), "/checkin/PC-01/")

    def test_checkout_url(self):
        self.assertEqual(reverse("checkout", kwargs={"pc_id": "PC-01"}), "/checkout/PC-01/")

    def test_status_url(self):
        self.assertEqual(reverse("status", kwargs={"pc_id": "PC-01"}), "/status/PC-01/")

    def test_feedback_url(self):
        self.assertEqual(
            reverse("feedback", kwargs={"pc_id": "PC-01", "software_id": 1}),
            "/feedback/PC-01/1/",
        )


class AdminUrlTest(TestCase):
    def test_login_url(self):
        self.assertEqual(reverse("login"), "/admin-portal/login/")

    def test_logout_url(self):
        self.assertEqual(reverse("logout"), "/admin-portal/logout/")

    def test_monitor_url(self):
        self.assertEqual(reverse("admin_monitor"), "/admin-portal/monitor/")

    def test_booking_url(self):
        self.assertEqual(reverse("admin_booking"), "/admin-portal/booking/")

    def test_booking_detail_url(self):
        self.assertEqual(reverse("admin_booking_detail", kwargs={"pk": 5}), "/admin-portal/booking/5/")

    def test_booking_import_url(self):
        self.assertEqual(reverse("admin_booking_import"), "/admin-portal/booking/import/")

    def test_manage_pc_url(self):
        self.assertEqual(reverse("admin_manage_pc"), "/admin-portal/manage-pc/")

    def test_add_pc_url(self):
        self.assertEqual(reverse("admin_add_pc"), "/admin-portal/manage-pc/add/")

    def test_edit_pc_url(self):
        self.assertEqual(
            reverse("admin_manage_pc_edit", kwargs={"pc_id": "PC-01"}),
            "/admin-portal/manage-pc/PC-01/edit/",
        )

    def test_delete_pc_url(self):
        self.assertEqual(
            reverse("admin_manage_pc_delete", kwargs={"pc_id": "PC-01"}),
            "/admin-portal/manage-pc/PC-01/delete/",
        )

    def test_software_url(self):
        self.assertEqual(reverse("admin_software"), "/admin-portal/software/")

    def test_software_edit_url(self):
        self.assertEqual(reverse("admin_software_edit", kwargs={"pk": 3}), "/admin-portal/software/3/edit/")

    def test_software_delete_url(self):
        self.assertEqual(reverse("admin_software_delete", kwargs={"pk": 3}), "/admin-portal/software/3/delete/")

    def test_report_url(self):
        self.assertEqual(reverse("admin_report"), "/admin-portal/report/")

    def test_report_export_url(self):
        self.assertEqual(reverse("admin_report_export"), "/admin-portal/report/export/")

    def test_config_url(self):
        self.assertEqual(reverse("admin_config"), "/admin-portal/config/")

    def test_user_url(self):
        self.assertEqual(reverse("admin_user"), "/admin-portal/users/")

    def test_user_edit_url(self):
        self.assertEqual(reverse("admin_user_edit", kwargs={"pk": 2}), "/admin-portal/users/2/edit/")

    def test_user_delete_url(self):
        self.assertEqual(reverse("admin_user_delete", kwargs={"pk": 2}), "/admin-portal/users/2/delete/")


# ══════════════════════════════════════════════════════════════════════════════
# 3. Login / Logout Tests — Django built-in LoginView/LogoutView พร้อมใช้แล้ว
# ══════════════════════════════════════════════════════════════════════════════

class LoginLogoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testadmin", password="testpass")

    def test_login_page_accessible(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_with_valid_credentials_redirects(self):
        response = self.client.post(
            reverse("login"),
            {"username": "testadmin", "password": "testpass"},
        )
        self.assertEqual(response.status_code, 302)

    def test_login_session_set_after_valid_login(self):
        self.client.post(
            reverse("login"),
            {"username": "testadmin", "password": "testpass"},
        )
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {"username": "testadmin", "password": "wrongpass"},
        )
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_redirects(self):
        self.client.login(username="testadmin", password="testpass")
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
