# ภานุวัฒน์ — Config (SiteConfig) + Admin User Management

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

# TODO: import render, redirect จาก django.shortcuts
# TODO: ถ้าต้องการจัดการ Django User ให้ใช้ User จาก django.contrib.auth.models

# TODO: Models ที่ต้องใช้จาก ..models
#   - SiteConfig   → ดึงและแก้ไขการตั้งค่าระบบ (lab_name, is_open, announcement ฯลฯ)
#   - AdminonDuty  → ดึงและแก้ไขข้อมูลเจ้าหน้าที่ประจำวัน


class AdminConfigView(LoginRequiredMixin, View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class AdminUserView(LoginRequiredMixin, View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class AdminUserEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        pass

    def post(self, request, pk):
        pass


class AdminUserDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        pass
