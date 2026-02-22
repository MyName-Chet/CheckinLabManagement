# อัษฎาวุธ — Booking Forms
from django import forms

from ..models import Booking, Computer


class BookingForm(forms.Form):
    student_id = forms.CharField(
        max_length=20,
        label="รหัสนักศึกษา",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "เช่น 66123456"}),
    )
    computer = forms.ModelChoiceField(
        queryset=Computer.objects.all().order_by("name"),
        empty_label="-- กรุณาเลือกเครื่อง --",
        label="เครื่องคอมพิวเตอร์",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    start_time = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        label="เวลาเริ่มใช้งาน",
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
    )
    end_time = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        label="เวลาสิ้นสุดการใช้งาน",
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
    )
    status = forms.ChoiceField(
        choices=Booking.STATUS_CHOICES,
        initial="APPROVED",
        label="สถานะ",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["computer"].queryset = Computer.objects.all().order_by("name")

    def clean(self):
        cleaned_data = super().clean()
        computer = cleaned_data.get("computer")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if not computer or not start_time or not end_time:
            return cleaned_data

        if end_time <= start_time:
            raise forms.ValidationError("เวลาสิ้นสุดต้องมากกว่าเวลาเริ่ม")

        is_conflict = Booking.objects.filter(
            computer=computer,
            status__in=["PENDING", "APPROVED"],
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()
        if is_conflict:
            raise forms.ValidationError("ช่วงเวลานี้มีการจองเครื่องนี้แล้ว")

        return cleaned_data


class ImportBookingForm(forms.Form):
    pass
