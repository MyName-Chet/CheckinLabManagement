# เขมมิกา — Report Forms
from django import forms

class ReportFilterForm(forms.Form):
    # ตัวเลือกสำหรับกลุ่มผู้ใช้งาน
    USER_TYPE_CHOICES = [
        ('all', 'ทั้งหมด (All Users)'),
        ('student', 'นักศึกษา (Student)'),
        ('staff', 'บุคลากร (Staff)'),
        ('guest', 'บุคคลภายนอก (Guest)'),
    ]

    # ตัวเลือกสำหรับรูปแบบเวลาในการ Export
    MODE_CHOICES = [
        ('daily', 'รายวัน'),
        ('monthly', 'รายเดือน'),
        ('quarterly', 'รายไตรมาส'),
        ('yearly', 'รายปี'),
    ]

    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        required=False,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    mode = forms.ChoiceField(
        choices=MODE_CHOICES,
        required=False,
        initial='daily',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    start_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    
    end_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # ตรวจสอบว่าถ้าส่งวันที่มาทั้งคู่ วันที่เริ่มต้นต้องไม่มากกว่าวันที่สิ้นสุด
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("วันที่เริ่มต้น ต้องไม่มากกว่าวันที่สิ้นสุด")
                
        return cleaned_data