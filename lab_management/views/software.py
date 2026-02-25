# ลลิดา — Software

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404

# นำเข้า Model
from lab_management.models import Software

# ✅ นำเข้า Form จากไฟล์ที่เราแยกไว้
from lab_management.forms.software import SoftwareForm

# ==========================================
# 💻 Views
# ==========================================

class AdminSoftwareView(LoginRequiredMixin, View):
    def get(self, request):
        # 1. ดึงข้อมูลซอฟต์แวร์ทั้งหมด
        softwares = Software.objects.all().order_by('-id') # เรียงจากใหม่ไปเก่า
        
        # 2. นับสถิติเพื่อไปโชว์ในการ์ดด้านบน
        total_count = softwares.count()
        ai_count = softwares.filter(type='AI').count()
        software_count = softwares.filter(type='Software').count()

        context = {
            'softwares': softwares,
            'total_count': total_count,
            'ai_count': ai_count,
            'software_count': software_count
        }
        return render(request, 'cklab/admin/admin-software.html', context)

    def post(self, request):
        # จัดการกรณีค่าว่างของวันที่
        mutable_post = request.POST.copy()
        if mutable_post.get('expire_date') == '':
            mutable_post['expire_date'] = None
            
        # สร้างรายการใหม่จากข้อมูลที่ส่งมาจาก Modal (แบบ POST)
        form = SoftwareForm(mutable_post)

        if form.is_valid():
            form.save() # บันทึกลง Database ทันที
            
        return redirect('admin_software')


class AdminSoftwareEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        # ดึงข้อมูล Software ตาม ID (pk) ถ้าไม่เจอให้แสดงหน้า 404
        software = get_object_or_404(Software, pk=pk)
        
        # นำข้อมูลเก่ามาใส่ฟอร์ม เพื่อนำไปโชว์ใน HTML (form.name.value)
        form = SoftwareForm(instance=software)
        
        return render(request, 'cklab/admin/admin-software-edit.html', {'form': form})

    def post(self, request, pk):
        # อัปเดตข้อมูลเก่า
        software = get_object_or_404(Software, pk=pk)
        
        mutable_post = request.POST.copy()
        if mutable_post.get('expire_date') == '':
            mutable_post['expire_date'] = None
            
        form = SoftwareForm(mutable_post, instance=software)
        
        if form.is_valid():
            form.save()
            return redirect('admin_software') # กลับไปหน้ารวมเมื่อเซฟเสร็จ
            
        # ถ้ากรอกข้อมูลไม่ถูกต้อง ให้โชว์หน้าเดิมพร้อมแจ้ง Error
        return render(request, 'cklab/admin/admin-software-edit.html', {'form': form})


class AdminSoftwareDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # ลบข้อมูล
        software = get_object_or_404(Software, pk=pk)
        software.delete()
        
        # กลับไปหน้าจัดการ Software
        return redirect('admin_software')