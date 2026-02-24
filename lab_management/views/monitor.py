import json
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

# นำเข้า Models ที่เกี่ยวข้อง
from lab_management.models import Computer, UsageLog, SiteConfig, Booking


# ==========================================
# 1. โหลดหน้าจอ Dashboard (HTML)
# ==========================================
class AdminMonitorView(LoginRequiredMixin, View):
    def get(self, request):
        config = SiteConfig.objects.first()
        return render(request, 'cklab/admin/admin-monitor.html', {'config': config})


# ==========================================
# 2. API สำหรับส่งข้อมูลสถานะเครื่องแบบ Real-time (JSON)
# ==========================================
class AdminMonitorDataAPIView(LoginRequiredMixin, View):
    def get(self, request):
        computers = Computer.objects.all().order_by('name')
        
        # ดึงประวัติคนที่กำลังใช้งานอยู่ทั้งหมด (ยังไม่ได้ Check-out)
        active_logs = UsageLog.objects.filter(end_time__isnull=True)
        active_users_map = {log.computer: log for log in active_logs}

        now = timezone.now()
        pc_list = []
        
        for pc in computers:
            user_name = ''
            elapsed_time = '00:00:00'
            next_booking_time = '-'
            
            # คำนวณเวลาที่ใช้งานไป (Elapsed Time) กรณีสถานะเป็น IN_USE
            if pc.status == 'IN_USE' and pc.name in active_users_map:
                log = active_users_map[pc.name]
                user_name = log.user_name
                
                diff = now - log.start_time
                hours, remainder = divmod(diff.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                elapsed_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            # ดึงเวลาคิวจองถัดไป (ถ้ามี)
            if pc.status in ['AVAILABLE', 'RESERVED']:
                next_booking = Booking.objects.filter(
                    computer=pc, 
                    status='APPROVED', 
                    start_time__gte=now
                ).order_by('start_time').first()
                
                if next_booking:
                    next_booking_time = next_booking.start_time.strftime("%H:%M")

            # ตรวจสอบซอฟต์แวร์
            is_ai = False
            software_name = '-'
            if pc.Software:
                software_name = pc.Software.name
                is_ai = (pc.Software.type == 'AI')

            pc_list.append({
                'id': pc.name,
                'name': pc.name,
                'status': pc.status,
                'user_name': user_name,
                'elapsed_time': elapsed_time,
                'next_booking_time': next_booking_time,
                'software': software_name,
                'is_ai': is_ai,
                'last_updated': pc.last_updated.strftime("%H:%M:%S") if pc.last_updated else '-'
            })

        # นับจำนวนสถานะทั้งหมด
        counts = {
            'AVAILABLE': computers.filter(status='AVAILABLE').count(),
            'IN_USE': computers.filter(status='IN_USE').count(),
            'RESERVED': computers.filter(status='RESERVED').count(),
            'MAINTENANCE': computers.filter(status='MAINTENANCE').count(),
            'total': computers.count(),
        }

        return JsonResponse({'status': 'success', 'pcs': pc_list, 'counts': counts})


# ==========================================
# 3. API สำหรับให้แอดมินบังคับ Check-in
# ==========================================
class AdminCheckinView(LoginRequiredMixin, View):
    def post(self, request, pc_id):
        pc = get_object_or_404(Computer, name=pc_id)
        
        # ป้องกันไม่ให้เช็คอินซ้อน
        if pc.status in ['IN_USE', 'MAINTENANCE']:
            return JsonResponse({'status': 'error', 'message': f'เครื่องนี้สถานะ {pc.status} ไม่สามารถเช็คอินได้'}, status=400)

        try:
            data = json.loads(request.body)
            user_id = data.get('user_id', 'AdminForce')
            user_name = data.get('user_name', 'Admin Force Check-in')
            department = data.get('department', '')
            user_type = data.get('user_type', 'guest')
            user_year = data.get('user_year', '')
        except:
            return JsonResponse({'status': 'error', 'message': 'รูปแบบข้อมูลไม่ถูกต้อง'}, status=400)

        # เปลี่ยนสถานะเครื่อง
        pc.status = 'IN_USE'
        pc.save()

        # เก็บชื่อซอฟต์แวร์ที่เครื่องนี้มี
        sw_name = pc.Software.name if pc.Software else None

        # บันทึกประวัติการใช้งาน
        UsageLog.objects.create(
            user_id=user_id,
            user_name=user_name,
            user_type=user_type,
            department=department,
            user_year=user_year,
            computer=pc.name,
            Software=sw_name
        )

        return JsonResponse({'status': 'success', 'message': f'เช็คอินเครื่อง {pc_id} สำเร็จ'})


# ==========================================
# 4. API สำหรับให้แอดมินบังคับ Check-out
# ==========================================
class AdminCheckoutView(LoginRequiredMixin, View):
    def post(self, request, pc_id):
        pc = get_object_or_404(Computer, name=pc_id)
        
        # ค้นหาประวัติการใช้งานที่ยังไม่สิ้นสุดของเครื่องนี้
        active_log = UsageLog.objects.filter(computer=pc.name, end_time__isnull=True).last()
        
        if active_log:
            active_log.end_time = timezone.now()
            active_log.save()

        # เคลียร์สถานะเครื่องให้กลับมาว่าง
        pc.status = 'AVAILABLE'
        pc.save()

        return JsonResponse({'status': 'success', 'message': f'เคลียร์เครื่อง {pc_id} ให้ว่างแล้ว'})