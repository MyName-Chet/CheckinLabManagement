from django.db import models 
from django.utils import timezone #แพนด้า
# ภานุวัฒน์ - สร้าง Model สำหรับการตั้งค่าระบบ (Config) เพื่อเก็บข้อมูลการตั้งค่าต่าง ๆ ของระบบ เจฝาก commit ครับ
class SiteConfig(models.Model):
    lab_name = models.CharField(max_length=255, default="CKLab", help_text="ชื่อห้องปฏิบัติการที่จะแสดงบนเว็บไซต์")
    booking_enabled = models.BooleanField(default=True, help_text="เปิด/ปิด การใช้งานระบบจอง")
    announcement = models.TextField(blank=True, null=True, help_text="ข้อความประกาศ (แสดงบนหน้า Kiosk)")
    location = models.CharField(max_length=255, blank=True, null=True, help_text="สถานที่ตั้ง (เช่น อาคาร 4 ชั้น 2)") #not sure if needed but can be useful for display on website
    admin_on_duty = models.ForeignKey('AdminonDuty', on_delete=models.SET_NULL, blank=True, null=True, help_text="เจ้าหน้าที่ดูแลระบบประจำวัน")
    is_open = models.BooleanField(default=True, help_text="สถานะการให้บริการห้องแล็บ (เปิด/ปิด)")
    feedback_url = models.CharField(max_length=500, blank=True, null=True, default='https://docs.google.com/forms/d/e/1FAIpQLSfnaw6G3NFsuKwngOenWfQ2pU3AQDAYbJ-ON1W5TpU8xjDeKw/viewform?embedded=true', help_text="ลิงก์แบบประเมิน (Google Form)")

class AdminonDuty(models.Model):
    contact_email = models.EmailField(blank=True, null=True, help_text="อีเมลติดต่อ (เช่น admin@example.com)") #not sure if needed but can be useful for display on website
    admin_on_duty = models.CharField(max_length=100, blank=True, null=True, help_text="เจ้าหน้าที่ดูแลระบบประจำวัน")
    contact_phone = models.CharField(max_length=50, blank=True, null=True, help_text="เบอร์โทรศัพท์ติดต่อ")

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
    user_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="ชื่อผู้จอง")
    # เชื่อมกับเครื่องคอมพิวเตอร์
    computer = models.ForeignKey('Computer', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="เครื่องคอมพิวเตอร์")
    
    # เวลาจอง
    start_time = models.DateTimeField(verbose_name="เวลาเริ่มใช้งาน")
    end_time = models.DateTimeField(verbose_name="เวลาสิ้นสุดการใช้งาน")
    booking_date = models.DateTimeField(default=timezone.now, verbose_name="วันที่ทำการจอง")
    
    # สถานะและการบันทึกเวลา (ใช้ default=timezone.now เหมือนตาราง ActivityLog)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="สถานะการจอง")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="เวลาที่ทำรายการ")


# ณัฐกรณ์ + ธนสิทธิ์ - ย้าย status เข้า Computer โดยตรง ไม่ต้องมี model Status แยก
class Computer(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'ว่าง (AVAILABLE)'),
        ('IN_USE', 'ใช้งาน (IN USE)'),
        ('RESERVED', 'จองแล้ว (RESERVED)'),
        ('MAINTENANCE', 'แจ้งซ่อม (MAINT.)'),
    ]

    name = models.CharField(max_length=20, unique=True, verbose_name="ชื่อเครื่อง")
    Software = models.ForeignKey(Software, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ซอฟต์แวร์ที่ติดตั้ง")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE', verbose_name="สถานะปัจจุบัน")
    # เพิ่มฟิลด์อัปเดตเวลาล่าสุด เพื่อให้ระบบรู้ว่าสถานะถูกเปลี่ยนไปเมื่อกี่วินาที/นาทีที่แล้ว (ช่วยเรื่อง Real-time)
    last_updated = models.DateTimeField(auto_now=True, verbose_name="อัปเดตสถานะล่าสุด")
    description = models.TextField(blank=True, null=True, verbose_name="รายละเอียดเพิ่มเติม")






# เขมมิกา - สร้าง Model สำหรับบันทึกการใช้งานคอมพิวเตอร์ (UsageLog)
class UsageLog(models.Model):
    # 1. ข้อมูลระบุตัวตนและประเภทผู้ใช้
    user_id = models.CharField(max_length=50)        # รหัสนักศึกษา/บุคลากร
    user_name = models.CharField(max_length=100)      # ชื่อ-นามสกุล
    user_type = models.CharField(max_length=20, choices=[('student', 'Student'), ('staff', 'Staff'),('guest', 'Guest')], null=True) # สถานะผู้ใช้ (Student/Staff)
    department = models.CharField(max_length=100, null=True, blank=True) # คณะ/หน่วยงาน
    user_year = models.CharField(max_length=10, null=True, blank=True)   # ชั้นปี

    # 2. ข้อมูลอุปกรณ์และซอฟต์แวร์
    # เชื่อมโยงกับ Computer เพื่อเก็บหมายเลขเครื่อง (pc_id/name)
    computer = models.CharField(max_length=20, null=True, blank=True) # ชื่อเครื่องคอมพิวเตอร์
    Software = models.CharField(max_length=100, null=True, blank=True) # ชื่อซอฟต์แวร์ที่ใช้ (ถ้ามี)

    # 3. วันที่และเวลา (รวมอยู่ในฟิลด์เดียวเพื่อความแม่นยำ)
    # เก็บทั้งวันที่และเวลาเริ่ม
    start_time = models.DateTimeField(auto_now_add=True) # บันทึกอัตโนมัติเมื่อ Checkin            
    # เก็บทั้งวันที่และเวลาสิ้นสุด (บันทึกอัตโนมัติเมื่อ Checkout)
    end_time = models.DateTimeField(null=True, blank=True) # อัปเดตเมื่อ Checkout

    # 4. การประเมินผลและข้อเสนอแนะ

    satisfaction_score = models.IntegerField(null=True, blank=True) # คะแนนความพึงพอใจ 1-5
    comment = models.TextField(null=True, blank=True)               # ข้อเสนอแนะเพิ่มเติม
