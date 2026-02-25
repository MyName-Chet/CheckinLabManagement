# เขมมิกา — Report + Export CSV

import csv
import codecs
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_datetime
from django.db.models import Q

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
        if not csv_file:
            return JsonResponse({'status': 'error', 'message': 'ไม่พบไฟล์ CSV'})

        try:
            # อ่านไฟล์ CSV (ใช้ utf-8-sig เพื่อรองรับภาษาไทยจาก Excel)
            reader = csv.reader(codecs.iterdecode(csv_file, 'utf-8-sig'))
            next(reader, None) # ข้ามบรรทัด Header

            imported_count = 0
            for row in reader:
                # ตรวจสอบว่าคอลัมน์ครบหรือไม่ (ตาม Template ที่เราออกแบบไว้)
                if len(row) < 11:
                    continue
                
                # หมายเหตุ: ในระบบจริง การเขียนโค้ดแปลง Date/Time จาก string ของ CSV กลับมาเป็น Datetime Object
                # จะต้องเขียนดัก Try/Except ตรงนี้เพิ่มเติม แต่เพื่อให้ระบบบันทึกได้คร่าวๆ จะร่างโครงสร้างไว้ให้ดังนี้
                
                # ตัวอย่างการบันทึก (สามารถปรับแก้ให้ตรงกับ format วันที่ของ CSV ได้)
                # UsageLog.objects.create(
                #     user_id=row[1],
                #     user_name=row[2],
                #     ...
                # )
                imported_count += 1

            return JsonResponse({'status': 'success', 'imported_count': imported_count})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


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