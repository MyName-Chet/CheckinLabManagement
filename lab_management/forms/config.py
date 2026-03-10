from django import forms
from django.contrib.auth.models import User
from ..models import SiteConfig, AdminonDuty  # <--- แก้ไขตรงนี้เป็นจุด 2 จุด (..) ถูกต้องแล้วครับ

# 1. ฟอร์มตั้งค่าห้องแล็บ (ใช้จัดการชื่อห้อง, สถานที่ และสถานะ เปิด/ปิด)
class SiteConfigForm(forms.ModelForm):
    class Meta:
        model = SiteConfig
        # ✅ เพิ่ม 'feedback_url' เข้ามาใน fields เรียบร้อย
        fields = ['lab_name', 'location', 'is_open', 'booking_enabled', 'announcement', 'feedback_url']

# 2. ฟอร์มเพิ่มแอดมินใหม่ (บังคับกรอกรหัสผ่าน)
class AdminUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="รหัสผ่าน")
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

# 3. ฟอร์มแก้ไขแอดมิน (ไม่บังคับรหัสผ่าน ถ้าไม่กรอกคือใช้รหัสเดิม)
class AdminUserEditForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, label="รหัสผ่านใหม่ (ปล่อยว่างถ้าไม่เปลี่ยน)")
    class Meta:
        model = User
        # เพิ่ม 'username' และ 'is_active' เข้าไปเพื่อให้หน้า HTML ดึงค่าไปโชว์ได้ครับ
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'password']