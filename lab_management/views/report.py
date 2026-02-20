# เขมมิกา — Report + Export CSV

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

# TODO: import render จาก django.shortcuts
# TODO: ถ้าต้องการ export CSV ให้ใช้ HttpResponse จาก django.http และ import csv (built-in)

# TODO: Models ที่ต้องใช้จาก ..models
#   - UsageLog  → ดึงประวัติการใช้งานทั้งหมด, filter ตาม date/user_type/software


class AdminReportView(LoginRequiredMixin, View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class AdminReportExportView(LoginRequiredMixin, View):
    def get(self, request):
        pass

    def post(self, request):
        pass
