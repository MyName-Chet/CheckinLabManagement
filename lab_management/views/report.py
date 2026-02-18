# เขมมิกา — Report + Export CSV
import csv
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import View
from ..models import UsageLog


class AdminReportView(LoginRequiredMixin, View):
    def get(self, request):
        pass


class AdminReportExportView(LoginRequiredMixin, View):
    def get(self, request):
        pass
