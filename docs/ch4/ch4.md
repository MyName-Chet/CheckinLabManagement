# บทที่ 4 การพัฒนาระบบ

บทนี้อธิบายรายละเอียดของการพัฒนาระบบ CKLab Management System ครอบคลุมเครื่องมือและเทคโนโลยีที่เลือกใช้ การออกแบบฐานข้อมูล (Models) การพัฒนา Business Logic (Views) การพัฒนา Frontend รวมถึงการแบ่งงานของสมาชิกในทีม

---

## 4.1 เครื่องมือและเทคโนโลยีที่ใช้

### 4.1.1 ภาพรวมเทคโนโลยี

ระบบ CKLab Management System ถูกพัฒนาด้วย Stack ที่ครบวงจร โดยแยกตาม Layer ได้ดังนี้

| Layer | เทคโนโลยี | เวอร์ชัน | เหตุผลที่เลือก |
|-------|-----------|---------|---------------|
| Backend Framework | Django | >=5.0, <6.0 | MVT pattern รองรับ CBV, ORM ครบถ้วน, ระบบ Auth ในตัว |
| Programming Language | Python | 3.10+ | รองรับ type hints, ecosystem ครบ, อ่านง่าย |
| Database | PostgreSQL | 15 (Docker) | ACID compliance, รองรับ concurrent access |
| Frontend CSS | Bootstrap | 5.3 | Responsive design, component library ครบ |
| Frontend Font | Google Fonts Kanit | — | รองรับภาษาไทยได้ดี, ดูเป็นระเบียบ |
| Container | Docker + Docker Compose | — | แยก environment, deploy ง่าย, Isolated PostgreSQL |
| Package Manager | uv (Astral) | — | เร็วกว่า pip หลายเท่า, resolves dependency ถูกต้อง |
| HTTP Client | requests + urllib3 | — | เรียก UBU External API, รองรับ verify=False สำหรับ SSL ภายใน |
| Env Config | python-dotenv | — | จัดการ SECRET_KEY, DB credentials ผ่าน .env file |
| DB Adapter | psycopg2-binary | — | Django ↔ PostgreSQL connector อย่างเป็นทางการ |
| VCS | Git + GitHub | — | Team collaboration, feature branch per member |

### 4.1.2 การตั้งค่า Docker Compose

ระบบใช้ Docker Compose สำหรับจัดการ services ในระหว่างการพัฒนา กำหนดไว้ในไฟล์ `docker-compose.yml` ดังนี้

- **service `db`** — PostgreSQL 15 พร้อม healthcheck เพื่อให้แน่ใจว่า database พร้อมก่อน Django เริ่ม
- **service `web`** — Django application ที่ `depends_on` service `db` เพื่อ start ตามลำดับ

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      retries: 5
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
```

การใช้ `condition: service_healthy` ทำให้ Django รอจนกว่า PostgreSQL จะพร้อมรับ connection จริง ป้องกันปัญหา "database not ready" เมื่อ start ระบบครั้งแรก

### 4.1.3 Dependencies หลัก (requirements.txt)

```
django>=5.0,<6.0
psycopg2-binary
python-dotenv
requests
urllib3
```

---

## 4.2 การพัฒนา Models (Database Layer)

Models ถูกกำหนดในไฟล์ `lab_management/models.py` ทั้งหมด 6 Model โดยแต่ละ Model รับผิดชอบโดยสมาชิกที่แตกต่างกัน

### 4.2.1 SiteConfig — การตั้งค่าระบบกลาง

*ผู้รับผิดชอบ: ภานุวัฒน์*

Model นี้ทำหน้าที่เป็น "กุญแจควบคุม" ของระบบ ทุกหน้าจะเรียก `SiteConfig.objects.first()` เพื่อดึงการตั้งค่าล่าสุด เมื่อ Admin เปลี่ยนค่าใดๆ ผลจะมีผลทันทีโดยไม่ต้อง restart server

```python
class SiteConfig(models.Model):
    lab_name = models.CharField(max_length=255, default="CKLab",
        help_text="ชื่อห้องปฏิบัติการที่จะแสดงบนเว็บไซต์")
    booking_enabled = models.BooleanField(default=True,
        help_text="เปิด/ปิด การใช้งานระบบจอง")
    is_open = models.BooleanField(default=True,
        help_text="สถานะการให้บริการห้องแล็บ (เปิด/ปิด)")
    announcement = models.TextField(blank=True, null=True,
        help_text="ข้อความประกาศ (แสดงบนหน้า Kiosk)")
    location = models.CharField(max_length=255, blank=True, null=True,
        help_text="สถานที่ตั้ง (เช่น อาคาร 4 ชั้น 2)")
    admin_on_duty = models.ForeignKey('AdminonDuty', on_delete=models.SET_NULL,
        blank=True, null=True, help_text="เจ้าหน้าที่ดูแลระบบประจำวัน")
```

**ฟิลด์สำคัญ:**
- `is_open` — ปิดห้องแล็บชั่วคราว: เมื่อ `False` ระบบ Kiosk จะปฏิเสธ Check-in ทุกกรณี
- `booking_enabled` — เปิด/ปิด feature การจองล่วงหน้า
- `announcement` — ข้อความแจ้งเตือนพิเศษที่แสดงบนหน้า Kiosk

### 4.2.2 AdminonDuty — ข้อมูลผู้ดูแลประจำวัน

*ผู้รับผิดชอบ: ภานุวัฒน์*

```python
class AdminonDuty(models.Model):
    admin_on_duty = models.CharField(max_length=100, blank=True, null=True,
        help_text="เจ้าหน้าที่ดูแลระบบประจำวัน")
    contact_email = models.EmailField(blank=True, null=True,
        help_text="อีเมลติดต่อ")
    contact_phone = models.CharField(max_length=50, blank=True, null=True,
        help_text="เบอร์โทรศัพท์ติดต่อ")
```

Model นี้มีความสัมพันธ์ ForeignKey กับ SiteConfig เพื่อแสดงชื่อและข้อมูลผู้ดูแลบนหน้า Kiosk

### 4.2.3 Software — ซอฟต์แวร์และ AI Tool

*ผู้รับผิดชอบ: ลลิดา*

```python
class Software(models.Model):
    TYPE_CHOICES = [
        ('Software', 'Software (ทั่วไป)'),
        ('AI', 'AI Tool (ปัญญาประดิษฐ์)'),
    ]
    name = models.CharField(max_length=100, verbose_name="ชื่อรายการ")
    version = models.CharField(max_length=50, verbose_name="แพ็กเกจ (Package)")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Software',
        verbose_name="ประเภท")
    expire_date = models.DateField(null=True, blank=True,
        verbose_name="วันหมดอายุ License")
```

**ประเด็นสำคัญ:** ฟิลด์ `type` รองรับ 2 ค่า (`Software` / `AI`) และแสดงผลต่างกันบน Monitor Dashboard — เครื่องที่ติดตั้ง AI Tool จะแสดง badge พิเศษ ช่วยให้ Admin รู้ว่าเครื่องไหนใช้สำหรับงาน AI

### 4.2.4 Computer — เครื่องคอมพิวเตอร์

*ผู้รับผิดชอบ: ณัฐกรณ์ + ธนสิทธิ์*

```python
class Computer(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'ว่าง (AVAILABLE)'),
        ('IN_USE', 'ใช้งาน (IN USE)'),
        ('RESERVED', 'จองแล้ว (RESERVED)'),
        ('MAINTENANCE', 'แจ้งซ่อม (MAINT.)'),
    ]
    name = models.CharField(max_length=20, unique=True, verbose_name="ชื่อเครื่อง")
    Software = models.ForeignKey(Software, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="ซอฟต์แวร์ที่ติดตั้ง")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
        default='AVAILABLE', verbose_name="สถานะปัจจุบัน")
    last_updated = models.DateTimeField(auto_now=True,
        verbose_name="อัปเดตสถานะล่าสุด")
    description = models.TextField(blank=True, null=True,
        verbose_name="รายละเอียดเพิ่มเติม")
```

**ฟิลด์สำคัญ:**
- `last_updated = auto_now=True` — อัปเดตทุกครั้งที่ `.save()` โดยอัตโนมัติ ช่วยให้ Monitor Dashboard รู้ว่าสถานะเปลี่ยนไปเมื่อใด
- `name = unique=True` — ชื่อเครื่องไม่ซ้ำกัน ใช้เป็น key อ้างอิงใน UsageLog

### 4.2.5 Booking — การจองล่วงหน้า

*ผู้รับผิดชอบ: อัษฎาวุธ*

```python
class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'รออนุมัติ'),
        ('APPROVED', 'อนุมัติแล้ว'),
        ('REJECTED', 'ไม่อนุมัติ/ยกเลิก'),
    ]
    student_id = models.CharField(max_length=20, verbose_name="รหัสนักศึกษา")
    computer = models.ForeignKey('Computer', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="เครื่องคอมพิวเตอร์")
    start_time = models.DateTimeField(verbose_name="เวลาเริ่มใช้งาน")
    end_time = models.DateTimeField(verbose_name="เวลาสิ้นสุดการใช้งาน")
    booking_date = models.DateTimeField(default=timezone.now,
        verbose_name="วันที่ทำการจอง")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
        default='PENDING', verbose_name="สถานะการจอง")
    created_at = models.DateTimeField(default=timezone.now,
        verbose_name="เวลาที่ทำรายการ")
```

Booking ใช้ ForeignKey ไปยัง Computer (ต่างจาก UsageLog) เพราะต้องการ query การจองตามเครื่องอย่างมีประสิทธิภาพ และสถานะของการจองจะถูกแสดงบน Monitor Dashboard ในส่วน "จองถัดไป" ของการ์ด PC แต่ละใบ

### 4.2.6 UsageLog — บันทึกการใช้งาน

*ผู้รับผิดชอบ: เขมมิกา*

```python
class UsageLog(models.Model):
    # ข้อมูลระบุตัวตน
    user_id = models.CharField(max_length=50)
    user_name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=20,
        choices=[('student','Student'),('staff','Staff'),('guest','Guest')], null=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    user_year = models.CharField(max_length=10, null=True, blank=True)

    # ข้อมูลอุปกรณ์ (Snapshot — ไม่ใช่ FK)
    computer = models.CharField(max_length=20, null=True, blank=True)
    Software = models.CharField(max_length=100, null=True, blank=True)

    # เวลา
    start_time = models.DateTimeField(auto_now_add=True)   # บันทึกอัตโนมัติเมื่อ Check-in
    end_time = models.DateTimeField(null=True, blank=True) # null = ยังใช้งานอยู่

    # ผลประเมิน
    satisfaction_score = models.IntegerField(null=True, blank=True)  # 1–5
    comment = models.TextField(null=True, blank=True)
```

**Design Decision — Snapshot Pattern:**

ฟิลด์ `computer` และ `Software` ใน UsageLog ถูกออกแบบให้เป็น `CharField` (เก็บชื่อเป็น text) แทนที่จะเป็น ForeignKey เหตุผลคือ:

- **รักษาความถูกต้องของประวัติ** — หากในอนาคต PC-05 ถูกลบออกจากระบบ หรือเปลี่ยน Software ใหม่ บันทึกการใช้งานเก่าๆ จะยังคงแสดงข้อมูลเดิมได้ถูกต้อง
- **ป้องกัน Cascade Delete** — หาก FK ชี้ไปที่ record ที่ถูกลบแล้ว Django จะมีปัญหา แต่ CharField ไม่ได้รับผลกระทบ
- **ข้อมูลประวัติสมบูรณ์** — Report และ Analytics สามารถ query ได้ครบถ้วนแม้ข้อมูลต้นทางจะเปลี่ยนแปลงไปแล้ว

---

## 4.3 การพัฒนา Views (Business Logic Layer)

ระบบแบ่ง Views ออกเป็น 8 module แยกตามฟังก์ชันการทำงาน ไฟล์อยู่ใน `lab_management/views/`

### 4.3.1 Kiosk Views (`lab_management/views/kiosk.py`)

*ผู้รับผิดชอบ: ปภังกร*

#### IndexView — Ghost State Detection & Auto-Fix

เมื่อผู้ใช้เปิดหน้า Kiosk ระบบจะตรวจสอบว่าเครื่องอยู่ในสถานะ IN_USE จริงหรือไม่ โดย query หา UsageLog ที่ยังไม่ได้ Check-out:

```python
class IndexView(View):
    def get(self, request):
        pc_name = request.GET.get('pc', 'PC-01')
        computer = Computer.objects.filter(name=pc_name).first()

        if computer and computer.status.upper() == 'IN_USE':
            active_log = UsageLog.objects.filter(
                computer=computer.name, end_time__isnull=True
            ).last()

            if active_log:
                # กรณีปกติ: เจอ session ที่ยังค้างอยู่
                # Auto-resume ไปหน้า Timer พร้อมเวลาเดิม
                start_time_ms = int(active_log.start_time.timestamp() * 1000)
                context = {
                    'computer': computer,
                    'log_id': active_log.id,
                    'start_time_ms': start_time_ms,
                    'user_name': active_log.user_name
                }
                return render(request, 'cklab/kiosk/timer.html', context)
            else:
                # Ghost State: สถานะค้าง IN_USE แต่ไม่มีคนนั่ง
                # Auto-Fix: ปรับสถานะกลับเป็น AVAILABLE อัตโนมัติ
                computer.status = 'AVAILABLE'
                computer.save()
```

Ghost State เกิดขึ้นเมื่อ Browser ปิดระหว่าง session หรือ session หมดอายุโดยไม่ได้ Check-out ระบบจะจัดการให้โดยอัตโนมัติโดยไม่ต้องให้ Admin เข้ามาแก้ไขด้วยตนเอง

#### VerifyUserAPIView — UBU External API Integration

```python
class VerifyUserAPIView(View):
    def post(self, request):
        body = json.loads(request.body)
        student_id = body.get('student_id', '').strip()

        # 1. เข้ารหัส student_id ด้วย Base64 ตามที่ UBU API กำหนด
        encoded_id = base64.b64encode(
            student_id.encode('utf-8')
        ).decode('utf-8')

        # 2. ส่ง POST request ไปยัง UBU External API
        response = requests.post(
            "https://esapi.ubu.ac.th/api/v1/student/reg-data",
            headers={"Content-Type": "application/json"},
            json={"loginName": encoded_id},
            timeout=10,
            verify=False  # ข้าม SSL เพราะ UBU ใช้ certificate ภายใน
        )

        # 3. คัดกรอง role จาก prefix ชื่อ
        staff_prefixes = ['อาจารย์', 'ดร.', 'ผศ.', 'รศ.', 'ศ.', 'นพ.', 'พญ.']
        role = 'student'
        if not student_id.isdigit() or any(prefix in full_name
                                            for prefix in staff_prefixes):
            role = 'staff'
```

API ของมหาวิทยาลัยต้องการ `loginName` เป็น Base64 ของ student_id การตรวจ role แยกบุคลากร (staff) ออกจากนักศึกษา (student) โดยใช้ 2 เงื่อนไข: รหัสไม่ใช่ตัวเลขล้วน หรือชื่อมี prefix ของอาจารย์/แพทย์

#### CheckinView, CheckoutView, FeedbackView

| View | HTTP | Action |
|------|------|--------|
| `CheckinView` | POST `/kiosk/<pc_id>/checkin/` | สร้าง UsageLog + Computer.status = IN_USE |
| `CheckoutView` | POST `/kiosk/<pc_id>/checkout/` | UsageLog.end_time = now() + Computer.status = AVAILABLE |
| `FeedbackView` | POST `/kiosk/<pc_id>/feedback/<log_id>/` | บันทึก satisfaction_score + comment ลงใน UsageLog |

### 4.3.2 Monitor Views (`lab_management/views/monitor.py`)

*ผู้รับผิดชอบ: ธนสิทธิ์*

#### AdminMonitorDataAPIView — Real-time JSON API

```python
class AdminMonitorDataAPIView(LoginRequiredMixin, View):
    def get(self, request):
        now = timezone.now()
        computers = Computer.objects.all().order_by('name')

        # Map UsageLog ที่ active เพื่อให้ lookup O(1)
        active_logs = UsageLog.objects.filter(end_time__isnull=True)
        active_users_map = {log.computer: log for log in active_logs}

        pc_list = []
        for pc in computers:
            if pc.status == 'IN_USE' and pc.name in active_users_map:
                log = active_users_map[pc.name]
                diff = now - log.start_time
                hours, remainder = divmod(int(diff.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                elapsed_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            # ... ดึง next_booking, software info และ append ลง pc_list

        return JsonResponse({
            'status': 'success',
            'pcs': pc_list,
            'bookings': booking_list,
            'counts': counts  # {AVAILABLE, IN_USE, RESERVED, MAINTENANCE, total}
        })
```

API นี้ถูกเรียกทุก 3 วินาทีโดย JavaScript ฝั่ง Frontend (AJAX Polling) และส่ง JSON response ที่มีข้อมูลสถานะเครื่อง, เวลาสะสม, การจองถัดไป และ summary counts สำหรับอัปเดต Dashboard

#### AdminCheckinView / AdminCheckoutView

Admin สามารถ Force check-in/out ผ่านหน้า Monitor Dashboard ได้โดยตรง โดย AdminCheckinView รับ JSON body พร้อม user_id, user_name, department และสร้าง UsageLog ใหม่ ส่วน AdminCheckoutView ค้นหา active log และบันทึก end_time

### 4.3.3 Booking Views (`lab_management/views/booking.py`)

*ผู้รับผิดชอบ: อัษฎาวุธ*

ระบบรองรับการจองทั้งแบบ Manual (ผ่าน Modal) และแบบ Bulk (ผ่าน CSV Import)

#### AdminImportBookingView — CSV Bulk Import

```python
class AdminImportBookingView(LoginRequiredMixin, View):
    def post(self, request):
        csv_file = request.FILES.get('csv_file')
        decoded_file = csv_file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded_file))

        for row in reader:
            # อ่านหัวคอลัมน์ภาษาไทย
            date_str = row.get('วันที่', '').strip()
            time_str = row.get('เวลา', '').strip()
            user_id  = row.get('ผู้จอง', '').strip()
            pc_name  = row.get('เครื่อง', '').strip()

            # รองรับวันที่ 2 รูปแบบ: DD/MM/YYYY และ YYYY-MM-DD
            if '/' in date_str:
                d_obj = datetime.strptime(date_str, '%d/%m/%Y')
            else:
                d_obj = datetime.strptime(date_str, '%Y-%m-%d')

            # สร้าง Booking ด้วยสถานะ APPROVED ทันทีสำหรับ Import
            Booking.objects.create(
                student_id=user_id,
                computer=computer,
                start_time=start_dt,
                end_time=end_dt,
                status='APPROVED'
            )
```

การ Import CSV ใช้ `utf-8-sig` encoding เพื่อรองรับ BOM ที่ Excel เพิ่มให้โดยอัตโนมัติ และ Booking ที่ Import เข้ามาจะได้รับสถานะ APPROVED ทันที เนื่องจาก Admin เป็นผู้นำเข้าข้อมูลเองโดยตรง ไม่ต้องผ่านขั้นตอนอนุมัติ

#### AdminBookingAddAPIView & AdminBookingStatusAPIView

| API View | Method | หน้าที่ |
|----------|--------|---------|
| `AdminBookingAddAPIView` | POST | รับ JSON จาก Modal → สร้าง Booking ใหม่ |
| `AdminBookingStatusAPIView` | POST | เปลี่ยนสถานะ PENDING → APPROVED / REJECTED |
| `AdminBookingDataAPIView` | GET | ส่ง JSON ข้อมูล Booking ทั้งหมดให้ JavaScript |
| `AdminBookingDetailView` | GET/POST | แสดงและอัปเดต Booking รายการเดียว |

### 4.3.4 Views Module อื่น ๆ

| Module | ไฟล์ | View Classes | ผู้รับผิดชอบ |
|--------|------|-------------|-------------|
| PC Management | `manage_pc.py` | AdminManagePCView, AdminPCDataAPIView, AdminPCAddAPIView, AdminPCEditAPIView | ณัฐกรณ์ |
| Software Management | `software.py` | AdminSoftwareView, AdminSoftwareDataAPIView, AdminSoftwareAddAPIView | ลลิดา |
| Reporting | `report.py` | AdminReportView, AdminReportDataAPIView, AdminExportCSVView | เขมมิกา |
| Config | `config.py` | AdminConfigView, AdminConfigSaveAPIView, AdminDutyAPIView, AdminUserAPIView | ภานุวัฒน์ |
| Authentication | `auth.py` | AdminLoginView, AdminLogoutView | สถาพร |

---

## 4.4 การพัฒนา Frontend

### 4.4.1 โครงสร้าง Template

ระบบใช้ Django Template Inheritance โดยมี `base.html` เป็น Parent Template ที่กำหนด structure หลัก ทุกหน้า extends ผ่าน `{% extends "base.html" %}`

Font หลักที่ใช้คือ **Kanit** จาก Google Fonts ซึ่งรองรับภาษาไทยได้ดีและมีน้ำหนักหลายระดับ (300, 400, 600) เหมาะกับ Dashboard ที่มีทั้ง header และ body text

ตาราง Templates หลักของระบบ:

| Template | URL Pattern | คำอธิบาย |
|----------|-------------|---------|
| `kiosk/index.html` | `/kiosk/?pc=PC-01` | หน้า Check-in: เลือก UBU WiFi หรือ Guest |
| `kiosk/timer.html` | (render หลัง Check-in) | หน้าแสดงเวลา session พร้อมปุ่ม Check-out |
| `kiosk/feedback.html` | `/kiosk/<pc>/feedback/<id>/` | หน้าให้คะแนนความพึงพอใจ 1–5 ดาว |
| `admin/admin-monitor.html` | `/admin-portal/monitor/` | Monitor Dashboard แสดงการ์ด PC ทุกเครื่อง |
| `admin/admin-booking.html` | `/admin-portal/booking/` | จัดการ Booking: เพิ่ม, อนุมัติ, ยกเลิก |
| `admin/admin-manage.html` | `/admin-portal/manage/` | จัดการเครื่อง PC: เพิ่ม, แก้ไข, เปลี่ยนสถานะ |
| `admin/admin-software.html` | `/admin-portal/software/` | จัดการ Software/AI Tool |
| `admin/admin-report.html` | `/admin-portal/report/` | รายงานการใช้งานและ Export CSV |
| `admin/admin-config.html` | `/admin-portal/config/` | ตั้งค่าระบบและข้อมูลผู้ดูแล |

### 4.4.2 timer.js — นับเวลา Session

*ไฟล์: `lab_management/static/cklab/js/timer.js`*

JavaScript ไฟล์นี้ทำหน้าที่นับเวลาการใช้งานแบบ real-time บนหน้า Timer

```javascript
// รับ SERVER_START_TIME จาก Django Template ผ่าน context variable
// ค่าเป็น Unix timestamp (milliseconds)
let startTime = Date.now();
if (typeof SERVER_START_TIME !== 'undefined' && SERVER_START_TIME > 0) {
    startTime = SERVER_START_TIME;
}

function updateTimer() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const hours   = Math.floor(elapsed / 3600);
    const minutes = Math.floor((elapsed % 3600) / 60);
    const seconds = elapsed % 60;

    document.getElementById('timer-display').textContent =
        `${String(hours).padStart(2,'0')}:` +
        `${String(minutes).padStart(2,'0')}:` +
        `${String(seconds).padStart(2,'0')}`;
}

timerInterval = setInterval(updateTimer, 1000);
```

**Design Decision — Server-side Start Time:**

เวลาเริ่มต้น (`start_time_ms`) ถูกส่งมาจาก Django View ใน context และ render ลงใน Template เป็น JavaScript variable ก่อนที่ Browser จะโหลดหน้า วิธีนี้ทำให้:
- **Auto-resume** — หาก Browser ปิดและเปิดใหม่ระหว่าง session เวลาจะนับต่อจากจุดที่ Check-in จริง ไม่ใช่เริ่มใหม่จาก 0
- **ความถูกต้อง** — เวลาอิงจาก Database ไม่ใช่ Browser clock ที่อาจต่างกันระหว่าง clients

### 4.4.3 auth.js — การยืนยันตัวตนผ่าน UBU API

*ไฟล์: `lab_management/static/cklab/js/auth.js`*

JavaScript ส่ง Fetch POST ไปยัง `/api/verify-user/` เพื่อตรวจสอบรหัสผู้ใช้ก่อนส่ง Check-in form

```javascript
async function verifyUBUUser(studentId) {
    const response = await fetch('/api/verify-user/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
                   'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ student_id: studentId })
    });
    const data = await response.json();

    if (data.status === 'success') {
        // แสดงชื่อ, คณะ, role ที่ตรวจสอบแล้ว
        // ใส่ข้อมูลลง hidden fields ของ form ก่อน submit
        fillCheckinForm(data.data);
    }
}
```

auth.js ยังจัดการ **Tab Toggle** — เมื่อผู้ใช้สลับระหว่าง "UBU WiFi Login" และ "Guest Login" สคริปต์จะแสดง/ซ่อน form ที่เกี่ยวข้อง และ clear ข้อมูลที่กรอกไว้

### 4.4.4 admin-monitor.js — Real-time AJAX Polling

*ไฟล์: `lab_management/static/cklab/js/admin-monitor.js`*

```javascript
const POLL_INTERVAL = 3000; // 3 วินาที

async function fetchMonitorData() {
    const response = await fetch('/admin-portal/api/monitor/data/');
    const data = await response.json();

    if (data.status === 'success') {
        updatePCCards(data.pcs);     // อัปเดตการ์ด PC ทุกใบ
        updateSummaryCards(data.counts); // อัปเดต Summary (ว่าง/ใช้/จอง/ซ่อม)
    }
}

function updatePCCards(pcs) {
    pcs.forEach(pc => {
        const card = document.getElementById(`pc-card-${pc.name}`);
        // อัปเดต: สีการ์ด, ชื่อผู้ใช้, เวลาสะสม, เวลาจองถัดไป, badge AI/Software
        card.className = `pc-card status-${pc.status.toLowerCase()}`;
        card.querySelector('.user-name').textContent = pc.user_name || '-';
        card.querySelector('.elapsed-time').textContent = pc.elapsed_time;
    });
}

setInterval(fetchMonitorData, POLL_INTERVAL);
fetchMonitorData(); // โหลดครั้งแรกทันทีโดยไม่รอ 3 วินาที
```

การใช้ AJAX Polling แทน WebSocket เป็น design decision ที่เหมาะสมกับ scale ของระบบ ลด complexity และไม่ต้องการ infrastructure เพิ่มเติม เพียงแค่ Django view ที่ return JSON ก็เพียงพอ

### 4.4.5 JavaScript Module อื่น ๆ

| ไฟล์ | หน้าที่ |
|------|---------|
| `feedback.js` | Star rating interactive (click เลือกดาว 1–5, highlight stars) |
| `admin-booking.js` | CRUD Booking ผ่าน Modal, filter ตามสถานะ, drag-and-drop calendar view |
| `admin-manage.js` | CRUD PC ผ่าน Modal, เปลี่ยนสถานะ, filter ตาม status |
| `admin-software.js` | CRUD Software/AI Tool ผ่าน Modal, filter ตาม type |
| `admin-report.js` | ดึงข้อมูลใช้งาน, วาด chart, Export CSV |
| `admin-config.js` | Save/Load ค่าตั้งค่าระบบผ่าน API, toggle เปิด/ปิดห้อง |

---

## 4.5 การแบ่งงานของสมาชิกในทีม

### 4.5.1 ตารางการแบ่งงาน

| สมาชิก | ความรับผิดชอบหลัก | View Module | Model ที่ดูแล |
|--------|------------------|-------------|--------------|
| ปภังกร | Kiosk UI, Check-in/out, Feedback, Ghost State Fix | `kiosk.py` (5 views) | — |
| สถาพร | ระบบ Authentication, Login/Logout | `auth.py` (2 views) | — |
| ภานุวัฒน์ | Config, User Management, Duty Admin | `config.py` (4 views) | `SiteConfig`, `AdminonDuty` |
| ธนสิทธิ์ | Monitor Dashboard, Real-time API, Force Check-in/out | `monitor.py` (4 views) | `Computer` (ร่วม) |
| อัษฎาวุธ | Booking System, CSV Import, Status Management | `booking.py` (6 views) | `Booking` |
| ณัฐกรณ์ | PC Management, CRUD, สถานะเครื่อง | `manage_pc.py` (4 views) | `Computer` |
| ลลิดา | Software/AI Tool Management | `software.py` (3 views) | `Software` |
| เขมมิกา | Reporting, Analytics, CSV Export | `report.py` (3 views) | `UsageLog` |

### 4.5.2 Git Workflow

ทีมใช้ **Feature Branch Workflow** โดยแต่ละสมาชิกสร้าง branch ของตัวเองแยกจาก `main`:

```
main
  ├── feature/kiosk           (ปภังกร)
  ├── feature/auth            (สถาพร)
  ├── feature/config          (ภานุวัฒน์)
  ├── feature/monitor         (ธนสิทธิ์)
  ├── feature/booking         (อัษฎาวุธ)
  ├── feature/manage-pc       (ณัฐกรณ์)
  ├── feature/software        (ลลิดา)
  └── feature/report          (เขมมิกา)
```

เมื่อพัฒนาแต่ละ feature เสร็จ สมาชิกสร้าง Pull Request เพื่อ code review ก่อน merge เข้า `main` วิธีนี้ช่วยป้องกัน merge conflict และให้ทีมสามารถพัฒนาแบบ parallel ได้โดยไม่กระทบกัน

### 4.5.3 โครงสร้างไฟล์โครงการ

```
CheckinLabManagement/
├── checkinlab/                  # Django Project settings
│   ├── settings.py
│   └── urls.py                  # Root URL configuration
├── lab_management/              # Main Django App
│   ├── models.py                # 6 Models (SiteConfig, Computer, ...)
│   ├── views/
│   │   ├── kiosk.py             # Kiosk: IndexView, CheckinView, ...
│   │   ├── monitor.py           # Monitor: AdminMonitorDataAPIView
│   │   ├── booking.py           # Booking: AdminImportBookingView, ...
│   │   ├── manage_pc.py         # PC Management
│   │   ├── software.py          # Software Management
│   │   ├── report.py            # Reporting & Export
│   │   ├── config.py            # System Config
│   │   └── auth.py              # Authentication
│   ├── forms/
│   │   ├── kiosk.py             # CheckinForm, FeedbackForm
│   │   └── booking.py           # BookingForm, ImportBookingForm
│   ├── templates/cklab/
│   │   ├── kiosk/               # 3 templates: index, timer, feedback
│   │   └── admin/               # 6+ templates: monitor, booking, ...
│   ├── static/cklab/
│   │   └── js/                  # 9 JavaScript files
│   └── urls.py                  # App-level URL patterns
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

---

*บทที่ 5 จะนำเสนอผลการทดสอบระบบและการประเมินผล*
