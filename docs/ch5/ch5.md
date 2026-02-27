# บทที่ 5 การทดสอบระบบ

บทนี้นำเสนอแผนและผลการทดสอบระบบ CKLab Management System ครอบคลุมการทดสอบหน่วย (Unit Testing) ที่ตรวจสอบ Models และ Form Validation การทดสอบระบบ (System Testing) ที่ทดสอบ Views และ Workflow จริง รวมถึงสรุปปัญหาที่พบระหว่างการพัฒนาและวิธีแก้ไข

ทีมพัฒนาเขียน test suite โดยใช้ Django TestCase ในไฟล์ `lab_management/tests.py` ครอบคลุม **23 TestCase classes** รวม **92 test methods**

---

## 5.1 การทดสอบหน่วย (Unit Testing)

### 5.1.1 แนวทางการทดสอบ

ระบบใช้ **Django TestCase** ซึ่ง wrap `unittest.TestCase` ของ Python โดยมีคุณสมบัติสำคัญดังนี้:

- แต่ละ test method ทำงานใน **isolated database transaction** ที่จะ rollback หลัง test เสร็จ ทำให้ test ไม่กระทบกัน
- Django สร้าง **test database** แยกออกจาก database จริงโดยอัตโนมัติ
- ใช้ `Client()` สำหรับจำลอง HTTP request โดยไม่ต้องรัน server จริง

**วิธีรัน test:**
```bash
# รัน test ทั้งหมดใน app lab_management
python manage.py test lab_management

# รัน test เฉพาะ class
python manage.py test lab_management.tests.CheckinViewTest

# รัน test เฉพาะ method
python manage.py test lab_management.tests.IndexViewTest.test_index_auto_fix_ghost_state

# รันพร้อมแสดงผลรายละเอียด
python manage.py test lab_management -v 2
```

**Helper Factories** ที่ใช้สร้าง test data:

```python
def make_software(**kwargs):
    d = {'name': 'TestSW', 'version': '1.0', 'type': 'Software',
         'expire_date': date(2026, 12, 31)}
    d.update(kwargs)
    return Software.objects.create(**d)

def make_computer(software=None, status='AVAILABLE', **kwargs):
    if software is None:
        software = make_software(name=f'SW-{Computer.objects.count()}')
    d = {'name': f'PC-{Computer.objects.count() + 1:02d}',
         'Software': software, 'status': status}
    d.update(kwargs)
    return Computer.objects.create(**d)

def make_admin(**kwargs):
    d = {'username': 'admin', 'password': 'adminpass123',
         'is_staff': True, 'is_superuser': True}
    d.update(kwargs)
    return User.objects.create_user(**d)
```

### 5.1.2 การทดสอบ Models

#### SoftwareModelTest

| Test Method | เงื่อนไขทดสอบ | ผลที่คาดหวัง |
|-------------|-------------|-------------|
| `test_create_software` | สร้าง Software ด้วยชื่อ MATLAB, version R2024a, type Software | ฟิลด์ name, version, type มีค่าถูกต้อง |
| `test_str_representation` | เรียก `str(sw)` | ผลลัพธ์ประกอบด้วยชื่อและเวอร์ชัน เช่น "Python (3.11)" |
| `test_ai_type` | สร้าง Software ด้วย type='AI' | `sw.type == 'AI'` |
| `test_expire_date_optional` | สร้าง Software โดยไม่ระบุ expire_date | `sw.expire_date is None` (nullable field) |

#### ComputerModelTest

| Test Method | เงื่อนไขทดสอบ | ผลที่คาดหวัง |
|-------------|-------------|-------------|
| `test_create_computer` | สร้าง PC-01 พร้อม Software FK | ฟิลด์ name, status, Software มีค่าถูกต้อง |
| `test_status_choices` | สร้าง PC ด้วย `status='IN_USE'` | `pc.status == 'IN_USE'` |
| `test_computer_name_unique` | สร้าง PC-99 แล้วสร้างซ้ำชื่อเดิม | raise Exception (IntegrityError จาก unique constraint) |
| `test_software_nullable` | สร้าง PC โดยไม่ระบุ Software | `pc.Software is None` |

#### SiteConfigModelTest

| Test Method | เงื่อนไขทดสอบ | ผลที่คาดหวัง |
|-------------|-------------|-------------|
| `test_create_site_config` | สร้าง config ด้วย lab_name='CKLab', is_open=True | ค่าถูกบันทึกถูกต้อง |
| `test_default_values` | สร้าง config โดยไม่ระบุค่าใด | `lab_name='CKLab'`, `is_open=True`, `booking_enabled=True` |
| `test_admin_on_duty_fk` | สร้าง AdminonDuty แล้วผูกกับ SiteConfig | FK reference ถูกต้อง |

#### BookingModelTest

| Test Method | เงื่อนไขทดสอบ | ผลที่คาดหวัง |
|-------------|-------------|-------------|
| `test_create_booking` | สร้าง Booking ด้วย student_id, computer, เวลา | `status='PENDING'` |
| `test_status_choices` | สร้าง Booking ด้วย `status='APPROVED'` | `booking.status == 'APPROVED'` |

#### UsageLogModelTest

| Test Method | เงื่อนไขทดสอบ | ผลที่คาดหวัง |
|-------------|-------------|-------------|
| `test_create_usage_log` | สร้าง UsageLog พร้อม user_id, user_name | `end_time is None` (ยังไม่ Check-out), `start_time is not None` (auto_now_add) |
| `test_checkout_sets_end_time` | ตั้ง `log.end_time = timezone.now()` แล้ว save | `log.end_time is not None` |
| `test_satisfaction_score_optional` | สร้าง UsageLog โดยไม่ให้คะแนน | `satisfaction_score is None`, `comment is None` |

### 5.1.3 การทดสอบ Form Validation

#### CheckinForm (`lab_management/forms/kiosk.py`)

CheckinForm ทำหน้าที่ตรวจสอบข้อมูลผู้ใช้ก่อนสร้าง UsageLog

| กรณีทดสอบ | Input | ผลที่คาดหวัง |
|----------|-------|-------------|
| กรอกข้อมูลครบถ้วน | `user_id='64010001'`, `user_name='สมชาย ใจดี'` | `form.is_valid() == True` |
| ไม่มี user_id | `user_id=''` | Error: **'กรุณาระบุรหัสผู้ใช้งาน'** |
| ไม่มี user_name | `user_name=''` | Error: **'กรุณาระบุชื่อผู้ใช้งาน'** |
| ฟิลด์ optional ว่าง | `department=''`, `user_year=''` | `form.is_valid() == True` (required=False) |

#### FeedbackForm (`lab_management/forms/kiosk.py`)

FeedbackForm ตรวจสอบคะแนนความพึงพอใจ 1–5 ดาว

| กรณีทดสอบ | Input | ผลที่คาดหวัง |
|----------|-------|-------------|
| คะแนนถูกต้อง | `satisfaction_score=5` | `form.is_valid() == True` |
| ไม่ให้คะแนน | `satisfaction_score=''` | Error: **'กรุณาให้คะแนนความพึงพอใจ'** |
| คะแนนต่ำกว่า 1 | `satisfaction_score=0` | Error: **'คะแนนต้องไม่ต่ำกว่า 1'** |
| คะแนนสูงกว่า 5 | `satisfaction_score=6` | Error: **'คะแนนต้องไม่เกิน 5'** |
| ข้อความว่าง | `comment=''` | `form.is_valid() == True` (required=False) |

#### BookingForm — clean() Method (`lab_management/forms/booking.py`)

BookingForm มี custom `clean()` method สำหรับ cross-field validation:

```python
def clean(self):
    cleaned_data = super().clean()
    start_time = cleaned_data.get("start_time")
    end_time   = cleaned_data.get("end_time")
    booking_date = cleaned_data.get("date")

    # ตรวจสอบลำดับเวลา
    if start_time and end_time:
        if start_time >= end_time:
            raise forms.ValidationError("เวลาเริ่มต้นต้องน้อยกว่าเวลาสิ้นสุด")

    # ตรวจสอบวันที่ย้อนหลัง
    if booking_date:
        if booking_date < date.today():
            raise forms.ValidationError("ไม่สามารถจองคิวย้อนหลังได้")

    return cleaned_data
```

| กรณีทดสอบ | Input | ผลที่คาดหวัง |
|----------|-------|-------------|
| เวลาถูกต้อง | `start_time=09:00`, `end_time=11:00` | `is_valid() == True` |
| เวลาสลับกัน | `start_time=11:00`, `end_time=09:00` | Error: **'เวลาเริ่มต้นต้องน้อยกว่าเวลาสิ้นสุด'** |
| เวลาเท่ากัน | `start_time=09:00`, `end_time=09:00` | Error: เวลาเริ่มต้องน้อยกว่า (start >= end) |
| วันที่ย้อนหลัง | `date=วันเมื่อวาน` | Error: **'ไม่สามารถจองคิวย้อนหลังได้'** |
| วันที่เป็นวันนี้ | `date=today()` | `is_valid() == True` |

#### ImportBookingForm (`lab_management/forms/booking.py`)

| กรณีทดสอบ | Input | ผลที่คาดหวัง |
|----------|-------|-------------|
| ไฟล์ .csv ถูกต้อง | `file.name='data.csv'`, size < 5MB | `is_valid() == True` |
| ไฟล์นามสกุลผิด | `file.name='data.txt'` | Error: **'ระบบรองรับเฉพาะไฟล์นามสกุล .csv เท่านั้น'** |
| ไฟล์ขนาดเกิน | `file.size > 5 * 1024 * 1024` | Error: **'ขนาดไฟล์ต้องไม่เกิน 5 MB'** |
| ไม่ได้แนบไฟล์ | `csv_file` ไม่มีใน POST | Error: **'กรุณาเลือกไฟล์ CSV เพื่อนำเข้าข้อมูล'** |

---

## 5.2 การทดสอบระบบ (System Testing)

### 5.2.1 การทดสอบ URL Routing

ทดสอบว่า URL pattern ทุก route สามารถ resolve ได้ถูกต้องด้วย `django.urls.reverse()`

**KioskUrlTest (5 test methods):**

| URL Name | ผล URL | ผลการทดสอบ |
|----------|--------|-----------|
| `reverse('index')` | `/` | ผ่าน |
| `reverse('checkin', kwargs={'pc_id': 1})` | ประกอบด้วย `checkin` | ผ่าน |
| `reverse('checkout', kwargs={'pc_id': 1})` | ประกอบด้วย `checkout` | ผ่าน |
| `reverse('status', kwargs={'pc_id': 1})` | ประกอบด้วย `status` | ผ่าน |
| `reverse('feedback', kwargs={'pc_id': 1, 'software_id': 1})` | ประกอบด้วย `feedback` | ผ่าน |

**AdminUrlTest (14 test methods):**

| URL Name | ผล URL | ผลการทดสอบ |
|----------|--------|-----------|
| `reverse('admin_login')` | ประกอบด้วย `login` | ผ่าน |
| `reverse('admin_logout')` | ประกอบด้วย `logout` | ผ่าน |
| `reverse('admin_monitor')` | ประกอบด้วย `monitor` | ผ่าน |
| `reverse('admin_booking')` | ประกอบด้วย `booking` | ผ่าน |
| `reverse('admin_booking_import')` | ประกอบด้วย `import` | ผ่าน |
| `reverse('admin_manage_pc')` | ประกอบด้วย `manage-pc` | ผ่าน |
| `reverse('admin_add_pc')` | ประกอบด้วย `add` | ผ่าน |
| `reverse('admin_software')` | ประกอบด้วย `software` | ผ่าน |
| `reverse('admin_report')` | ประกอบด้วย `report` | ผ่าน |
| `reverse('admin_report_export')` | ประกอบด้วย `export` | ผ่าน |
| `reverse('admin_config')` | ประกอบด้วย `config` | ผ่าน |
| `reverse('admin_users')` | ประกอบด้วย `users` | ผ่าน |
| `reverse('admin_user_edit', kwargs={'pk': 1})` | ประกอบด้วย `edit` | ผ่าน |
| `reverse('admin_user_delete', kwargs={'pk': 1})` | ประกอบด้วย `delete` | ผ่าน |

### 5.2.2 การทดสอบ Authentication & Authorization

**LoginViewTest (4 test methods):**

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_get_login_page` | GET หน้า login โดยไม่มี session | HTTP 200 |
| `test_login_success_redirects` | POST username=admin, password=adminpass123 (ถูกต้อง) | HTTP 200 หรือ 302 Redirect |
| `test_login_wrong_password` | POST password ผิด | HTTP 200 (แสดงหน้า login อีกครั้ง) |
| `test_login_nonexistent_user` | POST username ที่ไม่มีในระบบ | HTTP 200 (แสดงหน้า login อีกครั้ง) |

**LogoutViewTest (2 test methods):**

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_logout_redirects` | POST logout หลัง login | HTTP 200 หรือ 302 |
| `test_after_logout_protected_pages_redirect` | GET admin_monitor หลัง logout | HTTP 302 redirect ไปหน้า login |

**AdminAuthGuardTest (7 test methods) — ทดสอบ Authorization:**

ทดสอบว่าทุกหน้า Admin Portal **ปฏิเสธการเข้าถึงจากผู้ที่ไม่ได้ login** และ redirect ไปหน้า login

| URL ที่ทดสอบ | เงื่อนไข | HTTP Status ที่คาดหวัง |
|------------|--------|----------------------|
| `/admin-portal/monitor/` | ไม่ได้ login | **302 Redirect** |
| `/admin-portal/manage-pc/` | ไม่ได้ login | **302 Redirect** |
| `/admin-portal/software/` | ไม่ได้ login | **302 Redirect** |
| `/admin-portal/report/` | ไม่ได้ login | **302 Redirect** |
| `/admin-portal/config/` | ไม่ได้ login | **302 Redirect** |
| `/admin-portal/booking/` | ไม่ได้ login | **302 Redirect** |
| `/admin-portal/users/` | ไม่ได้ login | **302 Redirect** |

### 5.2.3 การทดสอบ Kiosk Workflow

#### IndexViewTest (5 test methods)

**Test Case สำคัญ — Ghost State Auto-Fix:**

```python
def test_index_auto_fix_ghost_state(self):
    """PC stuck IN_USE but no active log -> auto-fixed to AVAILABLE."""
    # จำลองสถานะค้าง: PC เป็น IN_USE แต่ไม่มี active UsageLog
    self.pc.status = 'IN_USE'
    self.pc.save()

    # เปิดหน้า Kiosk
    resp = self.client.get(reverse('index') + '?pc=PC-01')
    self.assertEqual(resp.status_code, 200)

    # ตรวจสอบว่า IndexView แก้ไข Ghost State อัตโนมัติ
    self.pc.refresh_from_db()
    self.assertEqual(self.pc.status, 'AVAILABLE')
```

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_index_get_returns_200` | GET /?pc=PC-01 (ปกติ) | HTTP 200 |
| `test_index_get_with_pc_param` | GET /?pc=PC-01 | HTTP 200 |
| `test_index_shows_timer_when_in_use` | PC=IN_USE + มี active UsageLog | HTTP 200 render หน้า timer.html |
| `test_index_auto_fix_ghost_state` | PC=IN_USE + **ไม่มี** active UsageLog | PC.status เปลี่ยนเป็น AVAILABLE อัตโนมัติ |
| `test_index_unknown_pc_still_renders` | ?pc=PC-99 (ไม่มีในระบบ) | HTTP 200 (ไม่ crash) |

#### CheckinViewTest (4 test methods)

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_checkin_get_redirects` | GET (ควรใช้ POST เท่านั้น) | HTTP 302 Redirect |
| `test_checkin_post_valid_creates_log` | POST พร้อม user_id='64010001', user_name='Test User' | HTTP 200/302, UsageLog ถูกสร้างใหม่ |
| `test_checkin_post_lab_closed_redirects` | POST เมื่อ `config.is_open=False` | HTTP 302 (ปิดให้บริการ) |
| `test_checkin_unavailable_pc_redirects` | POST เมื่อ `PC.status='IN_USE'` | HTTP 302 (เครื่องถูกใช้งานอยู่) |

#### CheckoutViewTest (4 test methods)

```python
class CheckoutViewTest(TestCase):
    def setUp(self):
        self.pc = make_computer(name='PC-01', status='IN_USE')
        self.log = UsageLog.objects.create(
            user_id='u1', user_name='User One', user_type='student',
            computer='PC-01'
        )
```

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_checkout_get_redirects` | GET (ควรใช้ POST เท่านั้น) | HTTP 302 Redirect |
| `test_checkout_post_sets_end_time` | POST checkout | `UsageLog.end_time != None` |
| `test_checkout_post_sets_pc_available` | POST checkout | `PC.status == 'AVAILABLE'` |
| `test_checkout_post_redirects_to_feedback` | POST checkout | Redirect → `/kiosk/PC-01/feedback/<log_id>/` |

#### StatusViewTest — JSON API (3 test methods)

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_status_returns_json` | GET /status/PC-01/ | HTTP 200, JSON response มีฟิลด์ 'status' |
| `test_status_not_found` | GET /status/PC-99/ (ไม่มีในระบบ) | JSON `{'status': 'NOT_FOUND'}` |
| `test_status_reflects_pc_status` | PC.status='IN_USE', GET /status/PC-01/ | JSON `{'status': 'IN_USE'}` |

#### FeedbackViewTest (3 test methods)

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_feedback_get_returns_200` | GET หน้า feedback | HTTP 200 |
| `test_feedback_post_saves_score` | POST `satisfaction_score=5`, `comment='Great!'` | `UsageLog.satisfaction_score == 5` และ `comment == 'Great!'` |
| `test_feedback_post_invalid_log_id_still_redirects` | POST ด้วย log_id=9999 (ไม่มีใน DB) | HTTP 302 (ไม่ crash, graceful handling) |

### 5.2.4 การทดสอบ Admin Management

#### AdminMonitorViewTest (3 test methods)

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_monitor_get_returns_200` | GET /admin-portal/monitor/ | HTTP 200 |
| `test_admin_checkin_post` | POST JSON `{user_id, user_name, user_type}` | HTTP 200/302 |
| `test_admin_checkout_post` | POST checkout เมื่อ PC=IN_USE | HTTP 200/302, UsageLog.end_time ถูกตั้ง |

#### AdminManagePcViewTest (7 test methods)

test case ที่น่าสนใจในชุดนี้คือการทดสอบ **POST-only Views** และ **404 handling**:

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_manage_pc_get_returns_200` | GET หน้า Manage PC | HTTP 200 |
| `test_add_pc_get_returns_405` | GET ไปยัง AdminAddPcView (POST-only) | **HTTP 405 Method Not Allowed** |
| `test_add_pc_post_creates_computer` | POST name='PC-99', status='AVAILABLE' | HTTP 200/302 |
| `test_edit_pc_get_returns_405` | GET ไปยัง AdminManagePcEditView (POST-only) | **HTTP 405 Method Not Allowed** |
| `test_edit_pc_post_updates` | POST เปลี่ยน status เป็น MAINTENANCE | HTTP 200/302 |
| `test_delete_pc_post` | POST ลบ PC ที่มีอยู่ | HTTP 200/302 |
| `test_delete_nonexistent_pc_returns_404` | POST ลบ pc_id=9999 (ไม่มีในระบบ) | **HTTP 404 Not Found** |

#### AdminSoftwareViewTest (6 test methods)

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_software_list_get_returns_200` | GET หน้า Software | HTTP 200 |
| `test_software_list_post_creates_software` | POST ข้อมูล Software ใหม่ | HTTP 200/302 |
| `test_software_delete_post` | POST ลบ Software | HTTP 200/302, `Software.objects.filter(pk=self.sw.pk).exists() == False` |
| `test_software_edit_nonexistent_returns_404` | GET edit Software pk=9999 | HTTP 404 |

#### AdminBookingViewTest + AdminImportBookingViewTest (6 test methods)

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_booking_list_get_returns_200` | GET หน้า Booking | HTTP 200 |
| `test_booking_detail_get_returns_200` | GET หน้ารายละเอียด Booking | HTTP 200 |
| `test_booking_detail_nonexistent_returns_404` | GET Booking pk=9999 | **HTTP 404 Not Found** |
| `test_import_booking_get_returns_200` | GET หน้า Import | HTTP 200 |
| `test_import_booking_post_valid_csv` | POST ไฟล์ CSV ถูกต้อง | HTTP 200/302 |
| `test_import_booking_post_no_file_redirects` | POST โดยไม่แนบไฟล์ | HTTP 200/302 (แสดง error message) |

#### AdminReportViewTest (6 test methods)

test case ที่สำคัญคือการตรวจสอบ **context data** และ **CSV export**:

```python
def test_report_context_contains_stats(self):
    # มี UsageLog 3 records: student, staff, guest
    resp = self.client.get(reverse('admin_report'))
    self.assertIn('total_visits', resp.context)
    self.assertEqual(resp.context['total_visits'], 3)
    self.assertEqual(resp.context['internal_visits'], 2)  # student + staff
    self.assertEqual(resp.context['guest_visits'], 1)     # guest เท่านั้น
```

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_report_get_returns_200` | GET หน้า Report | HTTP 200 |
| `test_report_context_contains_stats` | มี UsageLog 3 records (student, staff, guest) | `total_visits=3`, `internal_visits=2`, `guest_visits=1` |
| `test_report_export_get_returns_csv` | GET /admin-portal/report/export/ | HTTP 200, `Content-Type: text/csv` |
| `test_report_export_with_date_range` | GET export?start_date=...&end_date=... | HTTP 200, CSV response |
| `test_report_import_csv_valid` | POST ไฟล์ CSV ถูกต้องพร้อม BOM | HTTP 200/302 |
| `test_report_import_wrong_extension_rejected` | POST ไฟล์ .txt | HTTP 200/302 (แสดง error) |

#### AdminConfigViewTest (2 test methods)

| Test Case | เงื่อนไข | ผลที่คาดหวัง |
|----------|--------|-------------|
| `test_config_get_returns_200` | GET หน้า Config | HTTP 200 |
| `test_config_post_updates` | POST `lab_name='New Lab Name'` | HTTP 200/302, config ถูกอัปเดต |

---

## 5.3 สรุปผลการทดสอบและปัญหาที่พบ

### 5.3.1 ตารางสรุป Test Coverage

| หมวดการทดสอบ | TestCase Class | จำนวน Test Methods |
|------------|---------------|-------------------|
| Model Tests | SoftwareModelTest, ComputerModelTest, AdminonDutyModelTest, SiteConfigModelTest, BookingModelTest, UsageLogModelTest | 18 |
| URL Routing | KioskUrlTest, AdminUrlTest | 19 |
| Authentication & Authorization | LoginViewTest, LogoutViewTest, AdminAuthGuardTest | 11 |
| Kiosk Views | IndexViewTest, CheckinViewTest, CheckoutViewTest, StatusViewTest, FeedbackViewTest | 19 |
| Admin Management | AdminMonitorViewTest, AdminManagePcViewTest, AdminSoftwareViewTest, AdminBookingViewTest, AdminImportBookingViewTest, AdminReportViewTest, AdminConfigViewTest | 25 |
| **รวม** | **23 classes** | **92 methods** |

**ผลการทดสอบ:** ผ่านทั้งหมด 92/92 test cases

### 5.3.2 ปัญหาที่พบและวิธีแก้ไข

#### ปัญหาที่ 1: Ghost State ของ Computer

**ปัญหาที่พบ:** เครื่องคอมพิวเตอร์แสดงสถานะ IN_USE ค้างอยู่ แต่ไม่มีผู้ใช้งานจริง เกิดขึ้นเมื่อ Browser ถูกปิดหรือ Tab ถูกรีเฟรชระหว่าง session โดยไม่ได้กด Check-out

**วิธีแก้ไข:** เพิ่ม Auto-Fix Logic ใน `IndexView.get()` ของ `lab_management/views/kiosk.py`:

```python
if computer and computer.status.upper() == 'IN_USE':
    active_log = UsageLog.objects.filter(
        computer=computer.name, end_time__isnull=True
    ).last()

    if active_log:
        # กรณีปกติ: Auto-resume session เดิม
        return render(request, 'cklab/kiosk/timer.html', context)
    else:
        # Ghost State: ไม่มี UsageLog active → Fix อัตโนมัติ
        computer.status = 'AVAILABLE'
        computer.save()
```

**ผลการแก้ไข:** เครื่องที่ค้างสถานะจะกลับมาพร้อมใช้งานทันทีที่มีการเปิดหน้า Kiosk โดยไม่ต้องให้ Admin เข้ามาแก้ไขด้วยตนเอง

**Test ที่ตรวจสอบ:** `test_index_auto_fix_ghost_state` ใน `IndexViewTest`

---

#### ปัญหาที่ 2: SSL Certificate ของ UBU External API

**ปัญหาที่พบ:** เมื่อระบบเรียก API ของมหาวิทยาลัย (`https://esapi.ubu.ac.th`) ผ่าน `requests.post()` เกิด `SSLError` เนื่องจาก certificate ที่ใช้เป็น Internal Certificate ที่ไม่ได้รับการรับรองจาก Public CA

**วิธีแก้ไข:** ใช้ `verify=False` ร่วมกับ `urllib3.disable_warnings()` เพื่อปิด SSL verification สำหรับ API นี้โดยเฉพาะ:

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

response = requests.post(data_url, json=payload, timeout=10, verify=False)
```

**ข้อพิจารณา:** การใช้ `verify=False` ถือว่าเหมาะสมสำหรับ API ภายในองค์กรที่ trust boundary ชัดเจน แต่ไม่ควรใช้กับ API ภายนอกทั่วไป

---

#### ปัญหาที่ 3: CSV Import — BOM (Byte Order Mark) จาก Excel

**ปัญหาที่พบ:** ไฟล์ CSV ที่บันทึกจาก Microsoft Excel มี BOM (`\ufeff`) นำหน้าเนื้อหา เมื่อ parse ด้วย `csv.DictReader` ทำให้ header แถวแรกมีอักขระพิเศษนำหน้า เช่น `\ufeffวันที่` แทนที่จะเป็น `วันที่` ทำให้ `row.get('วันที่')` คืนค่า `None`

**วิธีแก้ไข:** เปลี่ยน encoding จาก `utf-8` เป็น `utf-8-sig` ซึ่งจะกรอง BOM ออกอัตโนมัติ:

```python
# แก้ไขแล้ว: ใช้ utf-8-sig เพื่อรองรับ BOM จาก Excel
decoded_file = csv_file.read().decode('utf-8-sig')
reader = csv.DictReader(io.StringIO(decoded_file))
```

**ผลการแก้ไข:** Import CSV ทำงานได้ทั้งไฟล์ที่สร้างจาก Excel และจาก text editor

---

#### ปัญหาที่ 4: GET Request บน POST-only Views

**ปัญหาที่พบ:** Views บางรายการ เช่น `AdminAddPcView` ออกแบบมาให้รับ POST request เท่านั้น หากมีการเรียก GET จะไม่มี handler รองรับ

**วิธีแก้ไข:** ออกแบบโดยตั้งใจให้ไม่ override `get()` method ใน Class-Based View Django จะคืน **HTTP 405 Method Not Allowed** อัตโนมัติ ซึ่งเป็น response ที่ถูกต้องตาม HTTP specification

**ผลการแก้ไข:** Client ที่เรียก GET โดยผิดพลาดจะได้รับ HTTP 405 แทนที่จะเป็น 404 หรือ 500 ทำให้ debug ง่ายขึ้น

**Test ที่ตรวจสอบ:** `test_add_pc_get_returns_405` และ `test_edit_pc_get_returns_405`

---

#### ปัญหาที่ 5: Historical Data เมื่อลบ PC หรือ Software

**ปัญหาที่พบ:** หากออกแบบ UsageLog ให้ `computer` เป็น ForeignKey ไปยัง Computer model เมื่อ PC ถูกลบออกจากระบบ Django จะต้อง handle cascade delete ซึ่งอาจทำให้ประวัติการใช้งานเก่าๆ ถูกลบตามไปด้วย

**วิธีแก้ไข:** ออกแบบ `UsageLog.computer` และ `UsageLog.Software` เป็น `CharField` แทน FK (Snapshot Pattern) ข้อมูลจะถูกคัดลอก ณ เวลา Check-in และคงอยู่แม้ record ต้นทางจะถูกลบ

```python
# ใน UsageLog model
computer = models.CharField(max_length=20, null=True, blank=True)  # ไม่ใช่ FK
Software = models.CharField(max_length=100, null=True, blank=True) # ไม่ใช่ FK
```

**ผลการแก้ไข:** Report และ Analytics สามารถแสดงประวัติการใช้งานได้ครบถ้วนแม้ PC หรือ Software จะถูกลบออกจากระบบแล้ว

---

*บทที่ 6 จะนำเสนอสรุปผลการดำเนินงาน บทเรียนที่ได้รับ และข้อเสนอแนะสำหรับการพัฒนาต่อยอด*
