# ภานุวัฒน์ — Config (SiteConfig)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from ..models import SiteConfig


class AdminConfigView(LoginRequiredMixin, View):
    def get(self, request):
        pass

    def post(self, request):
        pass
