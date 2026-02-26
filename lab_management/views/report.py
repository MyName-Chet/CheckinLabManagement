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
                score_str = row.get('คะแนน', '').strip()
                comment = row.get('ข้อเสนอแนะ', '').strip()

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
                # 3. แปลงคะแนน
                # ---------------------------------------------
                score = int(score_str) if score_str.isdigit() else None

                # ---------------------------------------------
                # 4. แปลง วันที่ และ เวลา 
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
                # 5. บันทึกลงฐานข้อมูล
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
                    end_time=end_dt,
                    satisfaction_score=score,
                    comment=comment
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
                'end_time': log.end_time.isoformat() if log.end_time else None,
                'satisfaction_score': log.satisfaction_score,
                'comment': log.comment
            })
            
        return JsonResponse({'logs': log_list})


# ==============================================================
# ระบบ Export Report ออกมาเป็นไฟล์ .csv โหลดลงเครื่อง
# ==============================================================
class AdminReportExportView(LoginRequiredMixin, View):
    def get(self, request):
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        logs = UsageLog.objects.all().order_by('-start_time')

        # หากมีการระบุช่วงเวลามาจากปุ่มในหน้าเว็บ (รายวัน, รายเดือน, รายปี)
        if start_date_str and end_date_str:
            start_date = parse_datetime(start_date_str)
            end_date = parse_datetime(end_date_str)
            if start_date and end_date:
                logs = logs.filter(start_time__gte=start_date, start_time__lte=end_date)

        # ตั้งค่า Header ให้เบราว์เซอร์รับรู้ว่าเป็นการดาวน์โหลดไฟล์ CSV
        response = HttpResponse(content_type='text/csv')
        
        # ตั้งชื่อไฟล์แบบมี Timestamp
        filename = f"CKLab_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # ฝัง BOM ลงไปที่จุดเริ่มต้นไฟล์ เพื่อบังคับให้ Excel อ่านภาษาไทยได้ถูกต้องเสมอ
        response.write(u'\ufeff'.encode('utf8'))

        writer = csv.writer(response)
        # เขียนหัวตาราง (Header)
        writer.writerow([
            'ลำดับ', 'รหัสผู้ใช้งาน', 'ชื่อ-สกุล', 'AI/Software ที่ใช้', 
            'วันที่ใช้บริการ', 'เวลาเข้า', 'เวลาออก', 'คณะ/หน่วยงาน', 
            'ชั้นปี', 'ประเภทผู้ใช้', 'PC ที่ใช้', 'คะแนนความพึงพอใจ', 'ข้อเสนอแนะ'
        ])

        # เขียนข้อมูลแต่ละแถว
        for idx, log in enumerate(logs, start=1):
            date_str = log.start_time.strftime('%d/%m/%Y') if log.start_time else '-'
            start_t = log.start_time.strftime('%H:%M') if log.start_time else '-'
            end_t = log.end_time.strftime('%H:%M') if log.end_time else '-'
            
            # แปลงประเภทผู้ใช้เป็นภาษาไทย
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
                log.computer or '-',
                log.satisfaction_score or '-',
                log.comment or '-'
            ])

        return response