# สถาพร — Login / Logout
from django.contrib.auth import views as auth_views

# TODO: Models ที่ต้องใช้จาก ..models
#   - AdminonDuty → อัปเดตข้อมูลผู้ดูแลเครื่องเมื่อ login / ล้างข้อมูลเมื่อ logout
#   - SiteConfig  → ผูก AdminonDuty เข้ากับ config ปัจจุบัน


class LoginView(auth_views.LoginView):
    template_name = 'cklab/admin/admin-login.html'

    # TODO: override form_valid() เพื่ออัปเดต AdminonDuty หลัง login สำเร็จ
    #   def form_valid(self, form):
    #       response = super().form_valid(form)
    #       # บันทึกชื่อ / เบอร์ / อีเมลของ admin ที่เพิ่ง login ลงใน AdminonDuty
    #       # ผูก SiteConfig.admin_on_duty = AdminonDuty ที่อัปเดต
    #       return response


class LogoutView(auth_views.LogoutView):
    next_page = '/admin-portal/login/'

    # TODO: override dispatch() เพื่อล้าง AdminonDuty ก่อน logout
    #   def dispatch(self, request, *args, **kwargs):
    #       # ล้างทุก field ของ AdminonDuty ที่ผูกกับ SiteConfig ปัจจุบัน:
    #       #   admin_on_duty = None, contact_phone = None, contact_email = None
    #       return super().dispatch(request, *args, **kwargs)
