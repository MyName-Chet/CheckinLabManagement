# อัษฎาวุธ — Booking

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

# TODO: import render, redirect จาก django.shortcuts

# TODO: Models ที่ต้องใช้จาก ..models
#   - Booking   → ดึงรายการจอง, สร้าง/แก้ไข/ลบการจอง
#   - Computer  → อัปเดต status เป็น RESERVED เมื่อมีการจอง, AVAILABLE เมื่อยกเลิก


class AdminBookingView(LoginRequiredMixin, View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class AdminBookingDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        pass

    def post(self, request, pk):
        pass


class AdminImportBookingView(LoginRequiredMixin, View):
    def post(self, request):
        pass
