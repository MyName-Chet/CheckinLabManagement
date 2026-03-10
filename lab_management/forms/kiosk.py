# ปภังกร — Kiosk Forms
from django import forms

class CheckinForm(forms.Form):
    # ฟิลด์ที่รับมาจากหน้า index.html (ตอนตรวจสอบรหัสเสร็จ)
    user_id = forms.CharField(
        max_length=20, 
        required=True, 
        error_messages={'required': 'กรุณาระบุรหัสผู้ใช้งาน'}
    )
    user_name = forms.CharField(
        max_length=150, 
        required=True, 
        error_messages={'required': 'กรุณาระบุชื่อผู้ใช้งาน'}
    )
    user_type = forms.CharField(max_length=50, required=False, initial='guest')
    department = forms.CharField(max_length=150, required=False, initial='-')
    user_year = forms.CharField(max_length=10, required=False, initial='-')
