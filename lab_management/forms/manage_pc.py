# ณัฐกรณ์ — Manage PC Forms
from django import forms
from lab_management.models import Computer, Software

class PcForm(forms.Form):
    # รับ ID ของเครื่องมาด้วย (เพื่อใช้เช็คกรณี Edit ว่าชื่อซ้ำกับเครื่องอื่นไหม แต่ไม่ซ้ำตัวเอง)
    pc_id = forms.IntegerField(
        required=False, 
        widget=forms.HiddenInput()
    )
    
    name = forms.CharField(
        max_length=20, 
        required=True,
        error_messages={'required': 'กรุณาระบุชื่อเครื่องคอมพิวเตอร์'}
    )
    
    status = forms.ChoiceField(
        choices=Computer.STATUS_CHOICES,
        required=True,
        initial='AVAILABLE',
        error_messages={'invalid_choice': 'สถานะไม่ถูกต้อง'}
    )
    
    # ใช้ ModelChoiceField เพื่อให้ฟอร์มเช็คอัตโนมัติว่า ID ของ Software ที่ส่งมามีจริงในระบบหรือไม่
    software_id = forms.ModelChoiceField(
        queryset=Software.objects.all(),
        required=False,
        empty_label="General (ไม่มี Software พิเศษ)"
    )

    def clean_name(self):
        """
        ฟังก์ชันสำหรับตรวจสอบข้อมูล (Validation) เฉพาะฟิลด์ name
        - ลบช่องว่างหน้า/หลัง
        - เช็คว่าชื่อเครื่องซ้ำใน Database หรือไม่
        """
        name = self.cleaned_data.get('name', '').strip()
        pc_id = self.cleaned_data.get('pc_id')
        
        # ค้นหาว่ามีเครื่องชื่อนี้อยู่แล้วไหม
        qs = Computer.objects.filter(name=name)
        
        # ถ้ามี pc_id ส่งมาด้วย แปลว่ากำลัง "แก้ไข (Edit)" ให้ยกเว้น ID ของตัวเอง
        if pc_id:
            qs = qs.exclude(id=pc_id)
            
        if qs.exists():
            raise forms.ValidationError(f"ชื่อเครื่อง '{name}' มีอยู่ในระบบแล้ว กรุณาใช้ชื่ออื่น")
            
        return name