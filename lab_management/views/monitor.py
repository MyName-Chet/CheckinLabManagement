import json
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.utils.timezone import localtime

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
# 2. API สำหรับส่งข้อมูลสถานะเครื่องและคิวจอง (Real-time JSON)
# ==========================================
class AdminMonitorDataAPIView(LoginRequiredMixin, View):
    def get(self, request):
        now = timezone.now()
        local_now = localtime(now)
        
        # ─── Midnight Reset Logic (Auto Force Checkout ข้ามวัน) ────────────────
        # กำหนดเวลาเที่ยงคืนของวันปัจจุบัน
        today_midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)

        # 1. ปิดจ๊อบ UsageLog ของคนที่ลืม Check-out ตั้งแต่เมื่อวาน
        stale_logs = UsageLog.objects.filter(end_time__isnull=True, start_time__lt=today_midnight)
        for log in stale_logs:
            log.end_time = today_midnight # ตัดจบเวลาใช้งานที่เที่ยงคืนตรง
            log.save()

        # 2. เคลียร์คิวจอง (Booking) ที่ค้างและหมดเวลาไปตั้งแต่เมื่อวาน
        Booking.objects.filter(
            status__in=['PENDING', 'APPROVED'], 
            end_time__lt=today_midnight
        ).update(status='REJECTED') 

        # 3. รีเซ็ตสถานะ Computer ที่ค้างเป็น IN_USE หรือ RESERVED มาจากเมื่อวาน
        stale_pcs = Computer.objects.filter(
            status__in=['IN_USE', 'RESERVED'],
            last_updated__lt=today_midnight
        )
        for pc in stale_pcs:
            pc.status = 'AVAILABLE'
            pc.save()
        # ─────────────────────────────────────────────────────────────────────

        # ดึงข้อมูลเครื่องทั้งหมดหลังจากรีเซ็ตสถานะเรียบร้อยแล้ว
        computers = Computer.objects.all().order_by('name')

        # ─── Auto-RESERVED / Auto-Revert Logic ───────────────────────────────
        window_start = now + timedelta(minutes=15)  
        no_show_cutoff = now - timedelta(minutes=15)  

        for pc in computers:
            if pc.status == 'AVAILABLE':
                upcoming = Booking.objects.filter(
                    computer=pc,
                    status='APPROVED',
                    start_time__lte=window_start,
                    start_time__gte=now,
                ).first()
                if upcoming:
                    pc.status = 'RESERVED'
                    pc.save()

            elif pc.status == 'RESERVED':
                active_log = UsageLog.objects.filter(computer=pc.name, end_time__isnull=True).last()
                if not active_log:
                    overdue = Booking.objects.filter(
                        computer=pc,
                        status='APPROVED',
                        start_time__lte=no_show_cutoff,
                        end_time__gte=now,
                    ).first()
                    if overdue:
                        pc.status = 'AVAILABLE'
                        pc.save()

        # รีเฟรช queryset หลังจาก Auto-Revert เผื่อมีการเปลี่ยนแปลง
        computers = Computer.objects.all().order_by('name')
        # ─────────────────────────────────────────────────────────────────────

        # 2.1 ดึงประวัติคนที่กำลังใช้งานอยู่ทั้งหมด
        active_logs = UsageLog.objects.filter(end_time__isnull=True)
        active_users_map = {log.computer: log for log in active_logs}

        pc_list = []
        for pc in computers:
            user_name = ''
            elapsed_time = '00:00:00'
            next_booking_time = '-'
            
            if pc.status == 'IN_USE' and pc.name in active_users_map:
                log = active_users_map[pc.name]
                user_name = log.user_name
                
                diff = now - log.start_time
                hours, remainder = divmod(int(diff.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                elapsed_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            next_booking = Booking.objects.filter(
                computer=pc, 
                status='APPROVED', 
                end_time__gte=now
            ).order_by('start_time').first()
            
            next_booking_start_iso = None
            next_booking_student_id = None
            if next_booking:
                local_next_start = localtime(next_booking.start_time)
                next_booking_time = local_next_start.strftime("%H:%M")
                next_booking_start_iso = local_next_start.isoformat()
                next_booking_student_id = next_booking.student_id

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
                'next_booking_start_iso': next_booking_start_iso,
                'next_booking_student_id': next_booking_student_id,
                'software': software_name,
                'is_ai': is_ai,
                'last_updated': localtime(pc.last_updated).strftime("%H:%M:%S") if pc.last_updated else '-'
            })

        # 2.2 ดึงข้อมูลคิวจองล่วงหน้าทั้งหมด
        future_bookings = Booking.objects.filter(
            status='APPROVED',
            end_time__gte=now
        ).order_by('start_time')

        booking_list = []
        for b in future_bookings:
            local_start = localtime(b.start_time)
            local_end = localtime(b.end_time)
            
            # 🌟 ดึงชื่อมาใช้งาน ถ้าไม่มีให้ใช้รหัสนักศึกษาแทน
            display_name = getattr(b, 'user_name', None) or b.student_id
            
            booking_list.append({
                'date': local_start.strftime('%d/%m/%Y'),
                'time': f"{local_start.strftime('%H:%M')} - {local_end.strftime('%H:%M')}",
                'pc_name': b.computer.name if b.computer else 'ไม่ระบุ',
                'user_id': b.student_id,
                'user_name': display_name, # 🌟 เพิ่มบรรทัดนี้ส่งไปให้ Monitor
                'status': b.status
            })

        # 2.3 นับจำนวนสถานะทั้งหมด
        counts = {
            'AVAILABLE': computers.filter(status='AVAILABLE').count(),
            'IN_USE': computers.filter(status='IN_USE').count(),
            'RESERVED': computers.filter(status='RESERVED').count(),
            'MAINTENANCE': computers.filter(status='MAINTENANCE').count(),
            'total': computers.count(),
        }

        return JsonResponse({
            'status': 'success', 
            'pcs': pc_list, 
            'bookings': booking_list, 
            'counts': counts
        })

# ==========================================
# 3. API สำหรับให้แอดมินบังคับ Check-in
# ==========================================
class AdminCheckinView(LoginRequiredMixin, View):
    def post(self, request, pc_id):
        pc = get_object_or_404(Computer, name=pc_id)
        
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

        pc.status = 'IN_USE'
        pc.save()

        sw_name = pc.Software.name if pc.Software else None

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
        
        active_log = UsageLog.objects.filter(computer=pc.name, end_time__isnull=True).last()
        
        if active_log:
            active_log.end_time = timezone.now()
            active_log.save()

        pc.status = 'AVAILABLE'
        pc.save()

        return JsonResponse({'status': 'success', 'message': f'เคลียร์เครื่อง {pc_id} ให้ว่างแล้ว'})