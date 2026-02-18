# ณัฐกรณ์ — Manage PC
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from ..models import Computer, Status


class AdminManagePcView(LoginRequiredMixin, View):
    def get(self, request):
        pass

    def post(self, request):
        pass
