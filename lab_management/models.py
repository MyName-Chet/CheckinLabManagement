from django.db import models 
from django.utils import timezone #แพนด้า
# ภานุวัฒน์ - สร้าง Model สำหรับการตั้งค่าระบบ (Config) เพื่อเก็บข้อมูลการตั้งค่าต่าง ๆ ของระบบ เจฝาก commit ครับ
class SiteConfig(models.Model):
    lab_name = models.CharField(max_length=255, default="CKLab", help_text="ชื่อห้องปฏิบัติการที่จะแสดงบนเว็บไซต์")
    booking_enabled = models.BooleanField(default=True, help_text="เปิด/ปิด การใช้งานระบบจอง")
    announcement = models.TextField(blank=True, null=True, help_text="ข้อความประกาศ (แสดงบนหน้า Kiosk)")
    location = models.CharField(max_length=255, blank=True, null=True, help_text="สถานที่ตั้ง (เช่น อาคาร 4 ชั้น 2)")
    contact_email = models.EmailField(blank=True, null=True, help_text="อีเมลติดต่อ (เช่น admin@example.com)")
    admin_on_duty = models.CharField(max_length=100, blank=True, null=True, help_text="เจ้าหน้าที่ดูแลระบบประจำวัน")
    contact_phone = models.CharField(max_length=50, blank=True, null=True, help_text="เบอร์โทรศัพท์ติดต่อ")
    is_open = models.BooleanField(default=True, help_text="สถานะการให้บริการห้องแล็บ (เปิด/ปิด)")
class Meta:
        verbose_name = "การตั้งค่าระบบ (Site Config)"
        verbose_name_plural = "การตั้งค่าระบบ (Site Config)"

def save(self, *args, **kwargs):
        self.pk = 1 
        super(SiteConfig, self).save(*args, **kwargs)

def __str__(self):
        return self.lab_name
    
    
# ลลิดา - สร้าง Model สำหรับ Software เพื่อเก็บข้อมูลซอฟต์แวร์ที่ติดตั้งในห้องปฏิบัติการ
class Software(models.Model):
    # ตัวเลือกประเภท (Dropdown) ให้ตรงกับใน JS
    TYPE_CHOICES = [
        ('Software', 'Software (ทั่วไป)'),
        ('AI', 'AI Tool (ปัญญาประดิษฐ์)'),
    ]

    # 1. ชื่อรายการ (ตรงกับ item.name)
    name = models.CharField(max_length=100, verbose_name="ชื่อรายการ")
    
    # 2. แพ็กเกจ / เวอร์ชัน (ตรงกับ item.version ใน JS / Package ในหน้าเว็บ)
    version = models.CharField(max_length=50, verbose_name="แพ็กเกจ (Package)")
    
    # 3. ประเภท (ตรงกับ item.type)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Software', verbose_name="ประเภท")
    
    # 4. วันหมดอายุ (ตรงกับ item.expire ใน JS)
    expire_date = models.DateField(null=True, blank=True, verbose_name="วันหมดอายุ License")

    def __str__(self):
        return f"{self.name} ({self.version})"
# อัษฎาวุธ - สร้าง Model สำหรับการจองคอมพิวเตอร์ (Booking) เพื่อเก็บข้อมูลการจองของผู้ใช้
class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'รออนุมัติ'),
        ('APPROVED', 'อนุมัติแล้ว'),
        ('REJECTED', 'ไม่อนุมัติ/ยกเลิก'),
    ]

    # ใช้รหัสนักศึกษาและชื่อเหมือนตาราง CheckinRecord ของเพื่อน
    student_id = models.CharField(max_length=20, verbose_name="รหัสนักศึกษา")
    student_name = models.CharField(max_length=100, verbose_name="ชื่อ-นามสกุลผู้จอง")
    
    # เชื่อมกับเครื่องคอมพิวเตอร์
    computer = models.ForeignKey('Computer', on_delete=models.CASCADE, verbose_name="เครื่องคอมพิวเตอร์")
    
    # เวลาจอง
    start_time = models.DateTimeField(verbose_name="เวลาเริ่มใช้งาน")
    end_time = models.DateTimeField(verbose_name="เวลาสิ้นสุดการใช้งาน")
    
    # สถานะและการบันทึกเวลา (ใช้ default=timezone.now เหมือนตาราง ActivityLog)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="สถานะการจอง")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="เวลาที่ทำรายการ")

    def __str__(self):
        return f"การจอง: {self.student_name} - {self.computer.name} ({self.get_status_display()})"


# ณัฐกรณ์ - สร้าง Model สำหรับสถานะเครื่องคอมพิวเตอร์ (Status) เพื่อระบุว่าเครื่องนั้นอยู่ในสถานะอะไร
class Status(models.Model):

    name = models.CharField(max_length=50, unique=True, verbose_name="ชื่อสถานะ")
    description = models.TextField(blank=True, null=True, verbose_name="รายละเอียดเพิ่มเติม")

    def __str__(self):
        return self.name

# ธนสิทธิ์ - สร้าง Model สำหรับคอมพิวเตอร์ (Computer) เพื่อเก็บข้อมูลสถานะและการใช้งานของคอมพิวเตอร์แต่ละเครื่องในห้องปฏิบัติการ
class Computer(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'ว่าง (AVAILABLE)'),
        ('IN_USE', 'ใช้งาน (IN USE)'),
        ('RESERVED', 'จองแล้ว (RESERVED)'),
        ('MAINTENANCE', 'แจ้งซ่อม (MAINT.)'),
    ]
    
    name = models.CharField(max_length=20, unique=True, verbose_name="ชื่อเครื่อง")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE', verbose_name="สถานะปัจจุบัน")
    
    # เพิ่มฟิลด์อัปเดตเวลาล่าสุด เพื่อให้ระบบรู้ว่าสถานะถูกเปลี่ยนไปเมื่อกี่วินาที/นาทีที่แล้ว (ช่วยเรื่อง Real-time)
    last_updated = models.DateTimeField(auto_now=True, verbose_name="อัปเดตสถานะล่าสุด")

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"


# 2. ตารางสำหรับการจองล่วงหน้า (มีคนจองช่วงเวลาไหน)
class Reservation(models.Model):
    student_id = models.CharField(max_length=20, verbose_name="รหัสนักศึกษา")
    student_name = models.CharField(max_length=100, verbose_name="ชื่อ-นามสกุลผู้จอง")
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, verbose_name="เครื่องที่จอง")
    
    # ระบุช่วงเวลาที่จอง
    start_time = models.DateTimeField(verbose_name="เวลาเริ่มจอง")
    end_time = models.DateTimeField(verbose_name="เวลาสิ้นสุดการจอง")
    
    is_active = models.BooleanField(default=True, verbose_name="สถานะการจอง (ยังใช้งานอยู่/ยกเลิกแล้ว)")

    def __str__(self):
        return f"จอง: {self.student_name} -> {self.computer.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"


# 3. ตารางบันทึกการเข้าใช้งานจริง (ใครเข้า-ออกเวลาไหน)
class CheckinRecord(models.Model):
    student_id = models.CharField(max_length=20, verbose_name="รหัสนักศึกษา")
    student_name = models.CharField(max_length=100, verbose_name="ชื่อ-นามสกุล")
    computer = models.ForeignKey(Computer, on_delete=models.SET_NULL, null=True, verbose_name="เครื่องคอมพิวเตอร์")
    ai_tool = models.CharField(max_length=50, blank=True, null=True, verbose_name="AI Tool ที่ใช้งาน")
    
    # บันทึกเวลาเข้าและออก
    checkin_time = models.DateTimeField(default=timezone.now, verbose_name="เวลาเข้าแล็บ")
    checkout_time = models.DateTimeField(blank=True, null=True, verbose_name="เวลาออกแล็บ")

    def __str__(self):
        pc_name = self.computer.name if self.computer else "ไม่ระบุ"
        return f"ใช้งาน: {self.student_name} - {pc_name}"


# 4. ตารางสำหรับเก็บประวัติการแจ้งเตือน (Notifications Feed)
class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('CHECK_IN', 'เข้าใช้งาน'),
        ('CHECK_OUT', 'ออกจากการใช้งาน'),
        ('RESERVE', 'ทำการจองเครื่อง'),
    ]
    
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="ประเภทกิจกรรม")
    message = models.CharField(max_length=255, verbose_name="รายละเอียดการแจ้งเตือน (เช่น นายสมชายเข้าใช้งาน PC-02)")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="เวลาที่เกิดเหตุการณ์")

    def __str__(self):
        return f"[{self.get_action_type_display()}] {self.message} ({self.timestamp.strftime('%H:%M:%S')})"

# เขมมิกา - สร้าง Model สำหรับบันทึกการใช้งานคอมพิวเตอร์ (UsageLog)
class UsageLog(models.Model):
    # 1. ข้อมูลระบุตัวตนและประเภทผู้ใช้
    user_id = models.CharField(max_length=50)        # รหัสนักศึกษา/บุคลากร
    user_name = models.CharField(max_length=100)      # ชื่อ-นามสกุล
    user_type = models.CharField(max_length=20, choices=[('student', 'Student'), ('staff', 'Staff')], null=True) # สถานะผู้ใช้ (Student/Staff)
    department = models.CharField(max_length=100, null=True, blank=True) # คณะ/หน่วยงาน
    user_year = models.CharField(max_length=10, null=True, blank=True)   # ชั้นปี

    # 2. ข้อมูลอุปกรณ์และซอฟต์แวร์
    # เชื่อมโยงกับ Computer เพื่อเก็บหมายเลขเครื่อง (pc_id/name)
    computer = models.ForeignKey('Computer', on_delete=models.SET_NULL, null=True) 
    software_used = models.CharField(max_length=100, null=True, blank=True)       # Software ที่ใช้งาน

    # 3. วันที่และเวลา (รวมอยู่ในฟิลด์เดียวเพื่อความแม่นยำ)
    # เก็บทั้งวันที่และเวลาเริ่ม
    start_time = models.DateTimeField()               
    # เก็บทั้งวันที่และเวลาสิ้นสุด (บันทึกอัตโนมัติเมื่อ Checkout)
    end_time = models.DateTimeField(auto_now_add=True)

    # 4. การประเมินผลและข้อเสนอแนะ
    satisfaction_score = models.IntegerField(null=True, blank=True) # คะแนนความพึงพอใจ 1-5
    comment = models.TextField(null=True, blank=True)               # ข้อเสนอแนะเพิ่มเติม

    class Meta:
        ordering = ['-end_time'] # เรียงจากใหม่ไปเก่าสำหรับหน้า Report

    def __str__(self):
        # แสดงชื่อผู้ใช้ คู่กับหมายเลขเครื่อง PC
        return f"{self.user_name} - {self.computer.name if self.computer else 'Unknown PC'}"