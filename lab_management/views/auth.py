# ปภังกร / สถาพร — Auth & User Management
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django import forms

# นำเข้า Models ที่ต้องใช้
from lab_management.models import SiteConfig, AdminonDuty

# ==========================================
# 1. ฟอร์มสำหรับแก้ไขข้อมูลแอดมิน
# ==========================================
class AdminUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']

# ==========================================
# 2. ระบบ Login / Logout (ของผู้รับผิดชอบ: ปภังกร)
# ==========================================
class LoginView(auth_views.LoginView):
    template_name = 'cklab/admin/admin-login.html'

    def form_valid(self, form):
        # ทำการ Login ให้สำเร็จก่อน
        response = super().form_valid(form)
        user = form.get_user()
        
        # ดึงหรือสร้าง Object SiteConfig และ AdminonDuty (ID=1 เพราะมีแค่อันเดียวในระบบ)
        config, _ = SiteConfig.objects.get_or_create(id=1)
        admin_duty, _ = AdminonDuty.objects.get_or_create(id=1)
        
        # อัปเดตข้อมูลผู้ดูแลเครื่องที่เพิ่งล็อกอิน
        admin_duty.admin_on_duty = user.get_full_name() or user.username
        admin_duty.contact_email = user.email
        admin_duty.contact_phone = "-" # ใส่ขีดไว้ก่อน
        admin_duty.save()

        # ผูกเข้ากับ SiteConfig
        config.admin_on_duty = admin_duty
        config.save()

        return response


class LogoutView(auth_views.LogoutView):
    # กำหนด URL Name ที่จะให้เด้งไปหลัง Logout
    next_page = 'admin_login'

    def dispatch(self, request, *args, **kwargs):
        # ดึง SiteConfig ปัจจุบัน
        config = SiteConfig.objects.filter(id=1).first()
        
        if config and config.admin_on_duty:
            # ล้างข้อมูลของ AdminonDuty เมื่อกดออกจากระบบ
            admin_duty = config.admin_on_duty
            admin_duty.admin_on_duty = None
            admin_duty.contact_phone = None
            admin_duty.contact_email = None
            admin_duty.save()

        # เคลียร์ Session ออกจากระบบ
        return super().dispatch(request, *args, **kwargs)


# ==========================================
# 3. ระบบจัดการแอดมิน Manage Users (ของผู้รับผิดชอบ: สถาพร / ภานุวัฒน์)
# ==========================================
class AdminUserView(LoginRequiredMixin, View):
    def get(self, request):
        # ดึงแอดมินทั้งหมดจากระบบ (เรียงคนใหม่สุดขึ้นก่อน)
        admin_users = User.objects.all().order_by('-id')
        
        context = {
            'admin_users': admin_users,
            'total_users': admin_users.count(),
            'active_users': admin_users.filter(is_active=True).count(),
        }
        return render(request, 'cklab/admin/admin-users.html', context)

    def post(self, request):
        # รับข้อมูลจาก Modal หน้าเว็บเพื่อสร้างบัญชีใหม่
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')

        if username and password:
            # ใช้ create_user เพื่อเข้ารหัสรหัสผ่านอัตโนมัติ
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    is_staff=True,
                    is_superuser=True # อนุญาตให้เข้าถึงหลังบ้านฐานข้อมูลได้
                )
        
        return redirect('admin_users')


class AdminUserEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        user_obj = get_object_or_404(User, pk=pk)
        form = AdminUserEditForm(instance=user_obj)
        return render(request, 'cklab/admin/admin-users-edit.html', {'form': form})

    def post(self, request, pk):
        user_obj = get_object_or_404(User, pk=pk)
        
        # คัดลอกค่า POST มาจัดการเรื่อง Checkbox สวิตช์เปิด-ปิด
        mutable_post = request.POST.copy()
        mutable_post['is_active'] = request.POST.get('is_active') == 'on'
        
        form = AdminUserEditForm(mutable_post, instance=user_obj)
        
        if form.is_valid():
            form.save()
            return redirect('admin_users')
            
        return render(request, 'cklab/admin/admin-users-edit.html', {'form': form})


class AdminUserDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user_obj = get_object_or_404(User, pk=pk)
        
        # ป้องกันไม่ให้แอดมินลบบัญชีตัวเองที่กำลังล็อกอินอยู่
        if user_obj.id != request.user.id:
            user_obj.delete()
            
        return redirect('admin_users')