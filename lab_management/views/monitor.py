# ธนสิทธิ์ — Admin Monitor Dashboard + API

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

# TODO: import render จาก django.shortcuts
# TODO: ถ้าต้องการ return JSON ให้ใช้ JsonResponse จาก django.http

# TODO: Models ที่ต้องใช้จาก ..models
#   - Computer  → ดึงรายการเครื่องทั้งหมดพร้อมสถานะ, อัปเดต status (IN_USE / AVAILABLE)


class AdminMonitorView(LoginRequiredMixin, View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class AdminCheckinView(LoginRequiredMixin, View):
    def post(self, request, pc_id):
        pass


class AdminCheckoutView(LoginRequiredMixin, View):
    def post(self, request, pc_id):
        pass
