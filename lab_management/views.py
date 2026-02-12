from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Computer, UsageLog

# ==========================================
# 1. ฝั่งผู้ใช้งาน (User / Kiosk Side)
# ==========================================

def index(request):
    """
    หน้าแรก Check-in (index.html)
    """
    # 1. รับค่า ID เครื่องจาก URL (เช่น ?pc=1) ถ้าไม่มีให้เป็น 1
    pc_id = request.GET.get('pc', '1')
    
    # 2. ดึงข้อมูลเครื่องจาก DB (ถ้าไม่มีให้สร้างใหม่กัน Error สำหรับการทดสอบ)
    computer, created = Computer.objects.get_or_create(
        pc_id=pc_id, 
        defaults={'name': f'PC-{pc_id}', 'status': 'available'}
    )
    
    # 3. ถ้ามีการกดปุ่ม Submit (POST) จากฟอร์ม
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        user_id = request.POST.get('user_id')
        
        # อัปเดตสถานะเครื่องใน Database
        computer.status = 'in_use'
        computer.current_user = user_name
        computer.session_start = timezone.now()
        computer.save()
        
        # ฝัง Session ไว้ใน Browser (เพื่อให้หน้า Timer รู้ว่าใครใช้)
        request.session['session_pc_id'] = computer.id
        request.session['session_user_name'] = user_name
        request.session['session_start_time'] = computer.session_start.isoformat()
        
        # ส่งไปหน้าจับเวลา
        return redirect('timer')

    # 4. ถ้าเป็นการเข้าหน้าเว็บปกติ (GET) ให้ส่งไฟล์ HTML ไปแสดง
    return render(request, 'cklab/kiosk/index.html', {'computer': computer})

def confirm(request):
    """
    หน้ายืนยันข้อมูล (confirm.html)
    """
    return render(request, 'cklab/kiosk/confirm.html')

def timer(request):
    """
    หน้าจับเวลา (timer.html)
    """
    # ตรวจสอบ Session ถ้าไม่มี (ไม่ได้ Check-in มา) ให้ดีดกลับหน้าแรก
    if 'session_pc_id' not in request.session:
        return redirect('index')

    context = {
        'user_name': request.session.get('session_user_name'),
        'start_time': request.session.get('session_start_time'),
    }
    return render(request, 'cklab/kiosk/timer.html', context)

def feedback(request):
    """
    หน้าประเมินผล (feedback.html) -> ทำหน้าที่ Checkout ด้วย
    """
    if request.method == 'POST':
        # 1. ดึง ID เครื่องจาก Session
        pc_id = request.session.get('session_pc_id')
        
        if pc_id:
            try:
                computer = Computer.objects.get(id=pc_id)
                
                # 2. บันทึก Log ลง Database ถาวร
                UsageLog.objects.create(
                    user_id="Unknown", # หรือดึงจาก session ถ้าเก็บไว้
                    user_name=request.session.get('session_user_name', 'Unknown'),
                    computer=computer,
                    start_time=computer.session_start or timezone.now(),
                    satisfaction_score=request.POST.get('rating', 0)
                )

                # 3. เคลียร์สถานะเครื่องให้ว่าง
                computer.status = 'available'
                computer.current_user = None
                computer.session_start = None
                computer.save()
            except Computer.DoesNotExist:
                pass

        # 4. ล้าง Session ทั้งหมดออกจาก Browser
        request.session.flush()
        
        # 5. กลับหน้าแรก
        return redirect('index')

    return render(request, 'cklab/kiosk/feedback.html')


# ==========================================
# 2. ฝั่งผู้ดูแลระบบ (Admin Portal Side)
# ==========================================

def admin_login(request):
    # ใช้ Template login ที่สร้างไว้
    return render(request, 'cklab/admin/admin-login.html')

@login_required
def admin_monitor(request):
    # ส่งข้อมูลเครื่องทั้งหมดไปแสดงผลเบื้องต้น
    computers = Computer.objects.all().order_by('pc_id')
    return render(request, 'cklab/admin/admin-monitor.html', {'computers': computers})

@login_required
def admin_booking(request):
    return render(request, 'cklab/admin/admin-booking.html')

@login_required
def admin_manage_pc(request):
    return render(request, 'cklab/admin/admin-manage.html')

@login_required
def admin_software(request):
    return render(request, 'cklab/admin/admin-software.html')

@login_required
def admin_report(request):
    return render(request, 'cklab/admin/admin-report.html')

@login_required
def admin_config(request):
    return render(request, 'cklab/admin/admin-config.html')


# ==========================================
# 3. API (สำหรับ JavaScript Fetch)
# ==========================================

def api_monitor_data(request):
    """
    API ส่งข้อมูลสถานะเครื่องเป็น JSON สำหรับหน้า Monitor (Real-time)
    """
    computers = Computer.objects.all().order_by('pc_id')
    data = []
    for pc in computers:
        data.append({
            'pc_id': pc.pc_id,
            'name': pc.name,
            'status': pc.status,
            'current_user': pc.current_user,
            'session_start': pc.session_start.isoformat() if pc.session_start else None
        })
    
    return JsonResponse({'status': 'ok', 'data': data})