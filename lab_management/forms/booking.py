# อัษฎาวุธ — Booking Forms
from django import forms
from datetime import date

class BookingForm(forms.Form):
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
    pc_name = forms.CharField(
        max_length=50, 
        required=True,
        error_messages={'required': 'กรุณาเลือกเครื่องคอมพิวเตอร์'}
    )
    date = forms.DateField(
        required=True,
        error_messages={'required': 'กรุณาระบุวันที่จอง', 'invalid': 'รูปแบบวันที่ไม่ถูกต้อง'}
    )
    start_time = forms.TimeField(
        required=True,
        error_messages={'required': 'กรุณาระบุเวลาเริ่มต้น', 'invalid': 'รูปแบบเวลาไม่ถูกต้อง'}
    )
    end_time = forms.TimeField(
        required=True,
        error_messages={'required': 'กรุณาระบุเวลาสิ้นสุด', 'invalid': 'รูปแบบเวลาไม่ถูกต้อง'}
    )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        booking_date = cleaned_data.get("date")

        # ตรวจสอบว่าเวลาเริ่ม ต้องน้อยกว่าเวลาสิ้นสุดเสมอ
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("เวลาเริ่มต้นต้องน้อยกว่าเวลาสิ้นสุด")

        # ตรวจสอบว่าห้ามจองย้อนหลัง
        if booking_date:
            if booking_date < date.today():
                raise forms.ValidationError("ไม่สามารถจองคิวย้อนหลังได้")

        return cleaned_data


class ImportBookingForm(forms.Form):
    csv_file = forms.FileField(
        required=True,
        error_messages={'required': 'กรุณาเลือกไฟล์ CSV เพื่อนำเข้าข้อมูล'}
    )

    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        
        # ตรวจสอบนามสกุลไฟล์ว่าต้องเป็น .csv เท่านั้น
        if file:
            if not file.name.endswith('.csv'):
                raise forms.ValidationError('ระบบรองรับเฉพาะไฟล์นามสกุล .csv เท่านั้น')
            
            # ตรวจสอบขนาดไฟล์ (เช่น ไม่เกิน 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('ขนาดไฟล์ต้องไม่เกิน 5 MB')
                
        return file