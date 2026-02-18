from django.db import models

# ภานุวัฒน์ - สร้าง Model สำหรับการตั้งค่าระบบ (Config) เพื่อเก็บข้อมูลการตั้งค่าต่าง ๆ ของระบบ
class SiteConfig(models.Model):
    lab_name = models.CharField(max_length=255)
    
# ลลิดา - สร้าง Model สำหรับ Software เพื่อเก็บข้อมูลซอฟต์แวร์ที่ติดตั้งในห้องปฏิบัติการ
class Software(models.Model):
    pass
# อัษฎาวุธ - สร้าง Model สำหรับการจองคอมพิวเตอร์ (Booking) เพื่อเก็บข้อมูลการจองของผู้ใช้
class Booking(models.Model):
    pass
# ณัฐกรณ์ - สร้าง Model สำหรับสถานะเครื่องคอมพิวเตอร์ (Status) เพื่อระบุว่าเครื่องนั้นอยู่ในสถานะอะไร
class Status(models.Model):
    pass

# ธนสิทธิ์ - สร้าง Model สำหรับคอมพิวเตอร์ (Computer) เพื่อเก็บข้อมูลสถานะและการใช้งานของคอมพิวเตอร์แต่ละเครื่องในห้องปฏิบัติการ
class Computer(models.Model):
    pass

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