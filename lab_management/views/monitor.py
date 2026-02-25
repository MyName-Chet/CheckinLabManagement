import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

# นำเข้า Models ที่เกี่ยวข้อง
from lab_management.models import Computer, UsageLog, SiteConfig

class AdminMonitorView(LoginRequiredMixin, View):
    def get(self, request):
        # 1. ตรวจสอบว่าเป็นการขอข้อมูลแบบ JSON (สำหรับ JS ดึงไปทำ Real-time Dashboard) หรือไม่
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json'
        
        if is_ajax:
            # ดึงข้อมูลเครื่องทั้งหมด
            computers = Computer.objects.all().order_by('name')
            
            # ดึงข้อมูลคนที่กำลังใช้งานอยู่ (end_time เป็น Null) เพื่อเอาชื่อมาโชว์ที่เครื่อง
            active_logs = UsageLog.objects.filter(end_time__isnull=True)
            active_users_map = {log.computer: log.user_name for log in active_logs}

            pc_list = []
            for pc in computers:
                pc_list.append({
                    'id': pc.name,
                    'name': pc.name,
                    'status': pc.status,
                    'user_name': active_users_map.get(pc.name, ''), # ดึงชื่อคนมาใส่ถ้ามี
                    'software': pc.Software.name if pc.Software else '-',
                    'last_updated': pc.last_updated.strftime("%H:%M:%S") if pc.last_updated else '-'
                })

            # นับจำนวนสรุป (✅ เพิ่ม reserved เข้าไป)
            counts = {
                'total': computers.count(),
                'available': computers.filter(status='AVAILABLE').count(),
                'in_use': computers.filter(status='IN_USE').count(),
                'reserved': computers.filter(status='RESERVED').count(),  # <-- เพิ่มบรรทัดนี้
                'maintenance': computers.filter(status='MAINTENANCE').count(),
            }

            return JsonResponse({'status': 'success', 'pcs': pc_list, 'counts': counts})

        # 2. ถ้าเป็นการเข้าเว็บปกติ ให้ Render หน้า HTML
        config = SiteConfig.objects.first()
        return render(request, 'cklab/admin/admin-monitor.html', {'config': config})

    def post(self, request):
        # เผื่ออนาคต: ใช้สำหรับให้ Admin สั่งเปลี่ยนสถานะหลายๆ เครื่องพร้อมกัน (Bulk Update)
        return JsonResponse({'status': 'error', 'message': 'Method Not Allowed'}, status=405)


class AdminCheckinView(LoginRequiredMixin, View):
    def post(self, request, pc_id):
        # แอดมินบังคับเช็คอินให้ (เช่น กรณีเด็กไม่ได้สแกนบัตร แต่เข้ามานั่ง)
        pc = get_object_or_404(Computer, name=pc_id)
        
        # ป้องกันไม่ให้เช็คอินซ้อนเครื่องที่ใช้งานอยู่ หรือเครื่องที่แจ้งซ่อม
        if pc.status in ['IN_USE', 'MAINTENANCE']:
            return JsonResponse({'status': 'error', 'message': f'เครื่องนี้สถานะ {pc.status} ไม่สามารถเช็คอินได้'})

        try:
            data = json.loads(request.body)
            user_id = data.get('user_id', 'AdminForce')
            user_name = data.get('user_name', 'Admin Force Check-in')
        except:
            user_id = 'AdminForce'
            user_name = 'Admin Force Check-in'

        # 1. เปลี่ยนสถานะเครื่อง
        pc.status = 'IN_USE'
        pc.save()

        # 2. บันทึกประวัติการใช้งาน
        UsageLog.objects.create(
            user_id=user_id,
            user_name=user_name,
            user_type='guest',
            computer=pc.name
            # start_time จะถูกบันทึกอัตโนมัติ (auto_now_add=True)
        )

        return JsonResponse({'status': 'success', 'message': f'เช็คอินเครื่อง {pc_id} สำเร็จ'})


class AdminCheckoutView(LoginRequiredMixin, View):
    def post(self, request, pc_id):
        # แอดมินบังคับคืนเครื่อง (Force Checkout)
        pc = get_object_or_404(Computer, name=pc_id)
        
        # 1. ค้นหาประวัติการใช้งานที่ยังไม่สิ้นสุดของเครื่องนี้
        active_log = UsageLog.objects.filter(computer=pc.name, end_time__isnull=True).first()
        
        if active_log:
            # 2. ลงเวลาสิ้นสุด
            active_log.end_time = timezone.now()
            active_log.save()

        # 3. เคลียร์สถานะเครื่องให้กลับมาว่าง
        pc.status = 'AVAILABLE'
        pc.save()

        return JsonResponse({'status': 'success', 'message': f'เคลียร์เครื่อง {pc_id} ให้ว่างแล้ว'})