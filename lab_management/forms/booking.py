# อัษฎาวุธ — Booking Forms
from django import forms
from lab_management.models import Booking, Computer

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['student_id', 'computer', 'start_time', 'end_time', 'status']
        
        # กำหนด Widgets เพื่อจัดการหน้าตาและคุณสมบัติของ Input
        widgets = {
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'รหัสนักศึกษา หรือ รหัสบุคลากร',
                'required': 'true'
            }),
            'computer': forms.Select(attrs={
                'class': 'form-select',
                'required': 'true'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': 'true'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': 'true'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        # กรองรายการคอมพิวเตอร์ให้เลือกเฉพาะเครื่องที่พร้อมใช้งาน (ไม่รวมเครื่องที่แจ้งซ่อม)
        self.fields['computer'].queryset = Computer.objects.exclude(status='MAINTENANCE').order_by('name')
        self.fields['computer'].empty_label = "-- เลือกหมายเลขเครื่อง (PC) --"

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        # ตรวจสอบว่าเวลาเลิกใช้งานต้องมากกว่าเวลาเริ่มใช้งาน
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError("❌ เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มต้น")
        
        return cleaned_data


class ImportBookingForm(forms.Form):
    csv_file = forms.FileField(
        label='เลือกไฟล์ CSV',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        })
    )