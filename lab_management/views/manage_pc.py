# ณัฐกรณ์ — Manage PC

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

# TODO: import render, redirect จาก django.shortcuts

# TODO: Models ที่ต้องใช้จาก ..models
#   - Computer  → ดึงรายการ PC ทั้งหมด, เพิ่ม/แก้ไข/ลบ PC
#   - Software  → ดึงรายการ Software เพื่อแสดงใน dropdown ตอนเพิ่ม/แก้ไข PC


class AdminManagePcView(LoginRequiredMixin, View):
    def get(self, request):
        pass


class AdminAddPcView(LoginRequiredMixin, View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class AdminManagePcEditView(LoginRequiredMixin, View):
    def get(self, request, pc_id):
        pass

    def post(self, request, pc_id):
        pass


class AdminManagePcDeleteView(LoginRequiredMixin, View):
    def post(self, request, pc_id):
        pass
