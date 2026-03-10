from django.contrib import admin
from .models import AdminonDuty, Booking, Computer, SiteConfig, Software, UsageLog

# ✅ อัปเกรดการแสดงผลหน้า Site Config ให้โชว์คอลัมน์สำคัญๆ เพื่อให้แอดมินดูง่ายขึ้น
@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    # กำหนดคอลัมน์ที่จะแสดงในหน้าตารางรวม
    list_display = ('lab_name', 'is_open', 'booking_enabled', 'feedback_url')
    # กำหนดช่องที่สามารถพิมพ์ค้นหาได้
    search_fields = ('lab_name',)

# ส่วนโมเดลอื่นๆ ลงทะเบียนแบบปกติ (หรือถ้าอยากแต่งเพิ่มก็ทำแบบข้างบนได้เลยครับ)
admin.site.register(AdminonDuty)
admin.site.register(Booking)
admin.site.register(Computer)
admin.site.register(Software)
admin.site.register(UsageLog)