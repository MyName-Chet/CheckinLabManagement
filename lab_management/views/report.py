# เขมมิกา — Report + Export CSV

import csv
import io
import codecs
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages

# Models ที่ต้องใช้
from lab_management.models import UsageLog

class AdminReportView(LoginRequiredMixin, View):
    def get(self, request):
        # 1. คำนวณตัวเลขสรุปภาพรวม (Lifetime Stats) ส่งไปให้ Template
        total_visits = UsageLog.objects.count()
        
        # นับจำนวนผู้ใช้ภายใน (นักศึกษา และ บุคลากร)
        internal_visits = UsageLog.objects.filter(user_type__in=['student', 'staff']).count()
        
        # นับจำนวนผู้ใช้ภายนอก
        guest_visits = UsageLog.objects.filter(user_type='guest').count()
        
        # คำนวณเปอร์เซ็นต์
        internal_percent = (internal_visits / total_visits * 100) if total_visits > 0 else 0
        guest_percent = (guest_visits / total_visits * 100) if total_visits > 0 else 0

        context = {
            'total_visits': total_visits,
            'internal_visits': internal_visits,
            'guest_visits': guest_visits,
            'internal_percent': round(internal_percent, 1),
            'guest_percent': round(guest_percent, 1),
        }
        return render(request, 'cklab/admin/admin-report.html', context)

    def post(self, request):
        # 2. ระบบ Import CSV (รับไฟล์มาจากหน้า Report)
        csv_file = request.FILES.get('csv_file')
        
        # เช็คว่ามีไฟล์ไหม และเป็น .csv หรือไม่
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, '❌ กรุณาอัปโหลดไฟล์นามสกุล .csv เท่านั้น')
            return redirect('admin_report')

        try:
            # อ่านไฟล์ CSV (ใช้ utf-8-sig เพื่อรองรับภาษาไทยจาก Excel)
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            imported_count = 0
            for row in reader:
                # ---------------------------------------------
                # 1. อ่านข้อมูลจากหัวคอลัมน์ "ภาษาไทย" ให้ตรงกับแบบฟอร์ม
                # ---------------------------------------------
                user_id = row.get('รหัสผู้ใช้', '').strip()
                user_name = row.get('ชื่อ-สกุล', '').strip()
                software = row.get('Software', '').strip()
                date_str = row.get('วันที่', '').strip()
                time_str = row.get('เวลา (เข้า-ออก)', '').strip()
                department = row.get('คณะ/หน่วยงาน', '').strip()
                user_year = row.get('ชั้นปี', '').strip()
                raw_type = row.get('ประเภท', '').strip()
                computer = row.get('PC', '').strip()

                # ถ้าแถวไหนว่างเปล่าจริงๆ ให้ข้ามไป
                if not user_id and not user_name:
                    continue

                # ---------------------------------------------
                # 2. แปลงประเภทผู้ใช้งาน
                # ---------------------------------------------
                if 'นักศึกษา' in raw_type: user_type = 'student'
                elif 'บุคลากร' in raw_type or 'อาจารย์' in raw_type: user_type = 'staff'
                else: user_type = 'guest'

                # ---------------------------------------------
                # 3. แปลง วันที่ และ เวลา 
                # (เช่น "17/01/2026" และ "09:00 - 10:30")
                # ---------------------------------------------
                start_dt = None
                end_dt = None
                if date_str and time_str:
                    try:
                        times = [t.strip() for t in time_str.split('-')]
                        start_t = times[0] if len(times) > 0 else '00:00'
                        end_t = times[1] if len(times) > 1 else start_t
                        
                        # รองรับวันที่ทั้งแบบ DD/MM/YYYY และ YYYY-MM-DD
                        if '/' in date_str:
                            d_obj = datetime.strptime(date_str, '%d/%m/%Y')
                        else:
                            d_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            
                        date_fmt = d_obj.strftime('%Y-%m-%d')
                        start_dt = timezone.make_aware(datetime.strptime(f"{date_fmt} {start_t}", '%Y-%m-%d %H:%M'))
                        end_dt = timezone.make_aware(datetime.strptime(f"{date_fmt} {end_t}", '%Y-%m-%d %H:%M'))
                    except Exception:
                        pass # ถ้ากรอกวันที่ผิดรูปแบบ ให้ข้ามไปใช้ค่า Auto

                # ---------------------------------------------
                # 4. บันทึกลงฐานข้อมูล
                # ---------------------------------------------
                # หมายเหตุ: start_time เป็น auto_now_add หากเราระบุค่าตอน .create() ทับลงไป บางครั้ง Django อาจจะเพิกเฉย
                # เลยต้องใช้วิธีสร้าง object ก่อนแล้วค่อยอัปเดต ถ้าอยากบันทึกข้อมูลย้อนหลังให้แม่นยำ
                log = UsageLog.objects.create(
                    user_id=user_id,
                    user_name=user_name,
                    user_type=user_type,
                    department=department,
                    user_year=user_year,
                    computer=computer,
                    Software=software,
                    end_time=end_dt
                )
                
                # เขียนทับ start_time อีกรอบเพื่อหลีกเลี่ยง auto_now_add
                if start_dt:
                    log.start_time = start_dt
                    log.save()
                    
                imported_count += 1

            messages.success(request, f'✅ นำเข้าข้อมูลสำเร็จ {imported_count} รายการ')
        except Exception as e:
            messages.error(request, f'❌ เกิดข้อผิดพลาดในการนำเข้าไฟล์: {str(e)}')

        return redirect('admin_report')


# ==============================================================
# [NEW] คลาสนี้ถูกสร้างเพิ่ม เพื่อใช้ปล่อยข้อมูล JSON ไปให้ JavaScript วาดกราฟ
# ==============================================================
class AdminReportAPIView(LoginRequiredMixin, View):
    def get(self, request):
        # ดึงประวัติทั้งหมดจากฐานข้อมูล (เรียงจากใหม่ไปเก่า)
        logs = UsageLog.objects.all().order_by('-start_time')
        
        log_list = []
        for log in logs:
            log_list.append({
                'id': log.id,
                'user_id': log.user_id,
                'user_name': log.user_name,
                'user_type': log.user_type,
                'department': log.department,
                'user_year': log.user_year,
                'computer': log.computer,
                'Software': log.Software,
                # แปลง Datetime เป็น string (ISO Format) เพื่อให้ JS นำไปแปลงต่อได้ง่าย
                'start_time': log.start_time.isoformat() if log.start_time else None,
                'end_time': log.end_time.isoformat() if log.end_time else None
            })
            
        return JsonResponse({'logs': log_list})


# ==============================================================
# ระบบ Export Report ออกมาเป็นไฟล์ .csv โหลดลงเครื่อง
# ==============================================================
class AdminReportExportView(LoginRequiredMixin, View):
    def get(self, request):
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        # 🌟 1. รับค่า department จาก URL ที่ JS ส่งมา (เช่น "คณะวิทยาศาสตร์,คณะศิลปศาสตร์")
        department_str = request.GET.get('department')

        logs = UsageLog.objects.all().order_by('-start_time')

        # 🌟 2. ถ้าระบุคณะ/หน่วยงานมา ให้กรองข้อมูลตามรายชื่อเหล่านั้นก่อน
        if department_str:
            # แปลง string เป็น list และลบคณะที่ว่างทิ้ง (ถ้ามีคนส่ง ,, มา)
            dept_list = [d.strip() for d in department_str.split(',') if d.strip()]
            if dept_list:
                # ใช้ Q object เพื่อกรองแบบ case-insensitive หรือตรงตัวใน list
                logs = logs.filter(department__in=dept_list)

        # 3. จัดการกรองวันที่ตามปกติ
        if start_date_str and end_date_str:
            try:
                # ตัดเอาเฉพาะ 10 ตัวแรก (YYYY-MM-DD) ป้องกันกรณี JS ส่งเวลาแปลกๆ ติดมา
                s_date = start_date_str[:10]
                e_date = end_date_str[:10]
                
                # แปลงเป็นออบเจกต์ Date
                start_dt_naive = datetime.strptime(s_date, '%Y-%m-%d')
                end_dt_naive = datetime.strptime(e_date, '%Y-%m-%d')

                # กำหนดเวลาให้ครอบคลุมทั้งวัน (00:00:00 - 23:59:59)
                start_dt_naive = start_dt_naive.replace(hour=0, minute=0, second=0)
                end_dt_naive = end_dt_naive.replace(hour=23, minute=59, second=59)

                # จัดการ Timezone (ถ้าโปรเจกต์เปิดใช้งาน USE_TZ)
                from django.conf import settings
                if getattr(settings, 'USE_TZ', False):
                    start_dt = timezone.make_aware(start_dt_naive)
                    end_dt = timezone.make_aware(end_dt_naive)
                else:
                    start_dt = start_dt_naive
                    end_dt = end_dt_naive

                # กรองข้อมูล (ใช้ __range เพื่อให้ครอบคลุมตั้งแต่ต้นจนจบวัน)
                logs = logs.filter(start_time__range=(start_dt, end_dt))
                
            except Exception as e:
                # ปริ้นท์บอกใน Terminal จะได้รู้ว่าพังตรงไหน หรือ JS ส่งอะไรมา
                print(f"🔥 [Export Error]: {e} | รับค่ามาเป็น: {start_date_str} ถึง {end_date_str}")
                pass 

        # ตั้งค่า Header ให้เบราว์เซอร์รับรู้ว่าเป็นการดาวน์โหลดไฟล์ CSV
        response = HttpResponse(content_type='text/csv')
        filename = f"CKLab_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # ฝัง BOM ลงไปที่จุดเริ่มต้นไฟล์ เพื่อบังคับให้ Excel อ่านภาษาไทยได้ถูกต้องเสมอ
        response.write(u'\ufeff'.encode('utf8'))

        writer = csv.writer(response)
        writer.writerow([
            'ลำดับ', 'รหัสผู้ใช้งาน', 'ชื่อ-สกุล', 'AI/Software ที่ใช้', 
            'วันที่ใช้บริการ', 'เวลาเข้า', 'เวลาออก', 'คณะ/หน่วยงาน', 
            'ชั้นปี', 'ประเภทผู้ใช้', 'PC ที่ใช้'
        ])

        for idx, log in enumerate(logs, start=1):
            date_str = log.start_time.strftime('%d/%m/%Y') if log.start_time else '-'
            start_t = log.start_time.strftime('%H:%M') if log.start_time else '-'
            end_t = log.end_time.strftime('%H:%M') if log.end_time else '-'
            
            role_display = 'บุคคลภายนอก'
            if log.user_type == 'student': role_display = 'นักศึกษา'
            elif log.user_type == 'staff': role_display = 'บุคลากร'

            writer.writerow([
                idx,
                log.user_id or '-',
                log.user_name or '-',
                log.Software or '-',
                date_str,
                start_t,
                end_t,
                log.department or '-',
                log.user_year or '-',
                role_display,
                log.computer or '-'
            ])

        return response