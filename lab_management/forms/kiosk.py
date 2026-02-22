# ปภังกร — Kiosk Forms
from django import forms

class CheckinForm(forms.Form):
    # ฟิลด์ที่รับมาจากหน้า index.html (ตอนตรวจสอบรหัสเสร็จ)
    user_id = forms.CharField(max_length=20, required=True)
    user_name = forms.CharField(max_length=150, required=True)
    user_type = forms.CharField(max_length=50, required=False)
    department = forms.CharField(max_length=150, required=False)
    user_year = forms.CharField(max_length=10, required=False)

class FeedbackForm(forms.Form):
    # ฟิลด์ที่รับมาจากหน้า feedback.html
    satisfaction_score = forms.IntegerField(min_value=1, max_value=5, required=True)
    comment = forms.CharField(widget=forms.Textarea, required=False)