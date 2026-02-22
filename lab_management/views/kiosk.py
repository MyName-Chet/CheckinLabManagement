import json
import base64
import requests
import urllib3
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.utils import timezone
from django.http import JsonResponse

# ปิดการแจ้งเตือนเรื่อง SSL เผื่อกรณี API มหาลัยใช้ Certificate ภายใน
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Models และ Forms ที่ต้องใช้
from lab_management.models import Computer, Software, SiteConfig, Booking, UsageLog
from lab_management.forms.kiosk import CheckinForm, FeedbackForm


class IndexView(View):
    def get(self, request):
        config = SiteConfig.objects.first()
        
        # บังคับใช้ PC-01 เป็นค่าเริ่มต้นหากไม่ได้ระบุใน URL
        pc_name = request.GET.get('pc')
        if not pc_name:
            pc_name = 'PC-01'
        
        context = {
            'config': config,
            'computer_name': pc_name
        }
        return render(request, 'cklab/kiosk/index.html', context)

    def post(self, request):
        pass


class StatusView(View):
    def get(self, request, pc_id):
        # API สำหรับคืนค่าสถานะเครื่องให้ Frontend เช็คแบบ Real-time
        computer = Computer.objects.filter(name=pc_id).first()
        if not computer:
            return JsonResponse({'status': 'NOT_FOUND', 'is_open': False})

        config = SiteConfig.objects.first()
        
        # ค้นหาการจองคิวถัดไป
        next_booking = Booking.objects.filter(
            computer=computer,
            status='APPROVED',
            start_time__gte=timezone.now()
        ).order_by('start_time').first()

        data = {
            'pc_id': computer.name,
            'status': computer.status,
            'is_open': config.is_open if config else False,
            'next_booking_start': next_booking.start_time.isoformat() if next_booking else None
        }
        return JsonResponse(data)


class VerifyUserAPIView(View):
    def post(self, request):
        try:
            body = json.loads(request.body)
            student_id = body.get('student_id', '').strip()

            if not student_id:
                return JsonResponse({'status': 'error', 'message': 'กรุณาระบุรหัสนักศึกษา'}, status=400)

            # 1. เข้ารหัสรหัสนักศึกษาเป็น Base64
            encoded_id = base64.b64encode(student_id.encode('utf-8')).decode('utf-8')

            # 2. ยิงตรงไปดึงข้อมูลนักศึกษา (ไม่ใช้ Token)
            data_url = "https://esapi.ubu.ac.th/api/v1/student/reg-data"
            headers = {
                "Content-Type": "application/json"
            }
            data_payload = {"loginName": encoded_id}
            
            # ใช้ verify=False เพื่อข้ามปัญหา SSL
            data_response = requests.post(data_url, headers=headers, json=data_payload, timeout=10, verify=False)
            
            # ✅ ยอมรับทั้ง 200 (OK) และ 201 (Created) ว่าทำงานสำเร็จ
            if data_response.status_code not in [200, 201]:
                error_msg = data_response.text
                return JsonResponse({'status': 'error', 'message': f'UBU API Connection Error ({data_response.status_code})'}, status=500)

            result = data_response.json()

            # ✅ เช็ค statusCode ข้างใน JSON เผื่อมหาลัยส่ง 201 มา
            if result.get('statusCode') in [200, 201] and result.get('data'):
                # ดึงข้อมูลตรงๆ เพราะ API ส่งมาเป็น Object 
                user_data = result['data'] 
                
                # ประกอบชื่อไทย
                full_name = f"{user_data.get('USERPREFIXNAME', '')}{user_data.get('USERNAME', '')} {user_data.get('USERSURNAME', '')}"
                
                # ดึงชั้นปีจาก API (STUDENTYEAR)
                student_year = str(user_data.get('STUDENTYEAR', '-'))

                return JsonResponse({
                    'status': 'success',
                    'data': {
                        'id': student_id,
                        'name': full_name.strip(),
                        'faculty': user_data.get('FACULTYNAME', 'มหาวิทยาลัยอุบลราชธานี'),
                        'role': 'student',
                        'level': user_data.get('LEVELNAME', 'ปริญญาตรี'),
                        'year': student_year
                    }
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'ไม่พบข้อมูลในระบบ (รหัสผิด หรือไม่ได้ลงทะเบียน)'}, status=404)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'status': 'error', 'message': f'Network Error: ตรวจสอบการเชื่อมต่อ VPN มหาวิทยาลัย'}, status=503)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'System Error: {str(e)}'}, status=500)


class CheckinView(View):
    def get(self, request, pc_id):
        return redirect(f"{reverse('kiosk_index')}?pc={pc_id}")

    def post(self, request, pc_id):
        computer = get_object_or_404(Computer, name=pc_id)
        config = SiteConfig.objects.first()
        
        if (config and not config.is_open) or computer.status not in ['AVAILABLE', 'RESERVED']:
            return redirect(f"{reverse('kiosk_index')}?pc={pc_id}&error=unavailable")

        # เรียกใช้ CheckinForm เพื่อกรองและตรวจสอบข้อมูลที่รับมา
        form = CheckinForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            
            # สร้างประวัติการใช้งานด้วยข้อมูลที่ผ่าน Form Validation แล้ว
            usage_log = UsageLog.objects.create(
                user_id=cleaned_data.get('user_id'),
                user_name=cleaned_data.get('user_name'),
                user_type=cleaned_data.get('user_type', 'student'),
                department=cleaned_data.get('department', ''),
                user_year=cleaned_data.get('user_year', ''),  
                computer=computer.name,
                Software=computer.Software.name if computer.Software else None
            )

            # อัปเดตสถานะเครื่อง
            computer.status = 'IN_USE'
            computer.save()

            return render(request, 'cklab/kiosk/timer.html', {'computer': computer, 'log_id': usage_log.id})
        else:
            # หากข้อมูลที่ส่งมาไม่ถูกต้อง ให้เด้งกลับไปหน้าแรก
            return redirect(f"{reverse('kiosk_index')}?pc={pc_id}&error=invalid_data")


class CheckoutView(View):
    def get(self, request, pc_id):
        return redirect(f"{reverse('kiosk_index')}?pc={pc_id}")

    def post(self, request, pc_id):
        computer = get_object_or_404(Computer, name=pc_id)
        usage_log = UsageLog.objects.filter(computer=computer.name, end_time__isnull=True).last()
        
        if usage_log:
            usage_log.end_time = timezone.now()
            usage_log.save()

        computer.status = 'AVAILABLE'
        computer.save()

        log_id = usage_log.id if usage_log else 0
        return redirect('kiosk_feedback', pc_id=computer.name, software_id=log_id)


class FeedbackView(View):
    def get(self, request, pc_id, software_id):
        context = {
            'pc_id': pc_id,
            'log_id': software_id  
        }
        return render(request, 'cklab/kiosk/feedback.html', context)

    def post(self, request, pc_id, software_id):
        # เรียกใช้ FeedbackForm เพื่อกรองข้อมูล
        form = FeedbackForm(request.POST)
        
        if form.is_valid():
            score = form.cleaned_data.get('satisfaction_score')
            comment = form.cleaned_data.get('comment', '')

            try:
                usage_log = UsageLog.objects.get(id=software_id)
                if score:
                    usage_log.satisfaction_score = score
                if comment:
                    usage_log.comment = comment
                usage_log.save()
            except UsageLog.DoesNotExist:
                pass

        return redirect(f"{reverse('kiosk_index')}?pc={pc_id}")