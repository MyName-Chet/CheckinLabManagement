# ณัฐกรณ์ — Manage PC

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

# นำเข้า Models และ Form ที่ต้องใช้
from lab_management.models import Computer, Software
from lab_management.forms import PcForm  # <--- ตรวจสอบ path ของ Form ให้ตรงกับโปรเจกต์คุณด้วยนะครับ

class AdminManagePcView(LoginRequiredMixin, View):
    def get(self, request):
        # ดึงข้อมูลเครื่อง PC ทั้งหมด เรียงตามชื่อ
        computers = Computer.objects.all().order_by('name')
        
        # ดึง Software ทั้งหมดเพื่อส่งไปแสดงในการ์ดเลือกซอฟต์แวร์
        softwares = Software.objects.all().order_by('name')
        
        context = {
            'computers': computers,
            'softwares': softwares,
        }
        return render(request, 'cklab/admin/admin-manage-pc.html', context)


class AdminAddPcView(LoginRequiredMixin, View):
    def post(self, request):
        # โยน request.POST เข้าไปให้ PcForm ตรวจสอบข้อมูล
        form = PcForm(request.POST)
        
        if form.is_valid():
            name = form.cleaned_data['name']
            status = form.cleaned_data['status']
            software_obj = form.cleaned_data['software_id'] # จะได้เป็น Object หรือ None อัตโนมัติ
            
            # บันทึกลง Database
            Computer.objects.create(
                name=name,
                status=status,
                Software=software_obj # ตัว S พิมพ์ใหญ่ตาม models.py
            )
            messages.success(request, f"เพิ่มเครื่อง '{name}' เข้าสู่ระบบเรียบร้อยแล้ว")
        else:
            # ถ้าข้อมูลไม่ผ่านการตรวจสอบ (เช่น ชื่อซ้ำ หรือไม่กรอกชื่อ) ให้แสดงแจ้งเตือน
            for error_list in form.errors.values():
                messages.error(request, error_list[0])
                
        return redirect('admin_manage_pc')


class AdminManagePcEditView(LoginRequiredMixin, View):
    def post(self, request, pc_id):
        pc = get_object_or_404(Computer, id=pc_id)
        
        # ก๊อปปี้ request.POST และยัด pc_id ใส่เข้าไป เพื่อให้ Form รู้ว่ายกเว้นการเช็คชื่อซ้ำของเครื่องตัวเอง
        post_data = request.POST.copy()
        post_data['pc_id'] = pc_id
        
        form = PcForm(post_data)
        
        if form.is_valid():
            pc.name = form.cleaned_data['name']
            pc.status = form.cleaned_data['status']
            pc.Software = form.cleaned_data['software_id']
            pc.save()
            
            messages.success(request, f"อัปเดตข้อมูลเครื่อง '{pc.name}' เรียบร้อยแล้ว")
        else:
            for error_list in form.errors.values():
                messages.error(request, error_list[0])
                
        return redirect('admin_manage_pc')


class AdminManagePcDeleteView(LoginRequiredMixin, View):
    def post(self, request, pc_id):
        pc = get_object_or_404(Computer, id=pc_id)
        pc_name = pc.name
        
        # สั่งลบเครื่อง
        pc.delete()
        
        messages.success(request, f"ลบเครื่อง '{pc_name}' ออกจากระบบสำเร็จ")
        return redirect('admin_manage_pc')