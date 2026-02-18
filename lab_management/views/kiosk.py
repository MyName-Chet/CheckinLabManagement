# ปภังกร — User / Kiosk Side
from django.views import View
from django.views.generic import TemplateView


class IndexView(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class ConfirmView(TemplateView):
    template_name = 'cklab/kiosk/confirm.html'


class TimerView(View):
    def get(self, request):
        pass


class FeedbackView(View):
    def get(self, request):
        pass

    def post(self, request):
        pass
