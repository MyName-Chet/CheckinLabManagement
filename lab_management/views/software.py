# ลลิดา — Software

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

# TODO: import render, redirect จาก django.shortcuts

# TODO: Models ที่ต้องใช้จาก ..models
#   - Software  → ดึงรายการ Software ทั้งหมด, เพิ่ม/แก้ไข/ลบ Software


class AdminSoftwareView(LoginRequiredMixin, View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class AdminSoftwareEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        pass

    def post(self, request, pk):
        pass


class AdminSoftwareDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        pass
