# ปภังกร — User / Kiosk Side

# TODO: ต้องใช้ View จาก django.views และ redirect, render จาก django.shortcuts
from django.views import View

# TODO: Models ที่ต้องใช้จาก ..models
#   - Computer   → ดึงข้อมูลสถานะเครื่อง, อัปเดต status
#   - Software   → ดึงชื่อซอฟต์แวร์ที่ติดตั้งในเครื่อง
#   - SiteConfig → ดึงค่า config (is_open, announcement, booking_enabled)
#   - Booking    → ค้นหาการจองถัดไปของเครื่อง (next_booking_end)
#   - UsageLog   → สร้าง record เมื่อ Checkout + บันทึกคะแนน


class IndexView(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class StatusView(View):
    def get(self, request, pc_id):
        pass


class CheckinView(View):
    def get(self, request, pc_id):
        pass

    def post(self, request, pc_id):
        pass


class CheckoutView(View):
    def get(self, request, pc_id):
        pass

    def post(self, request, pc_id):
        pass


class FeedbackView(View):
    def get(self, request, pc_id, software_id):
        pass

    def post(self, request, pc_id, software_id):
        pass
