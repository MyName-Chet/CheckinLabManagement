# ลลิดา — Software Forms

from django import forms
from lab_management.models import Software

class SoftwareForm(forms.ModelForm):
    class Meta:
        model = Software
        fields = ['name', 'version', 'type', 'expire_date']
        
        # กำหนด Widget เผื่อนำไป Render ด้วยคำสั่ง {{ form }} ในอนาคต
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อรายการ'}),
            'version': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เวอร์ชัน หรือ แพ็กเกจ'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'expire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }