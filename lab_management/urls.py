from django.urls import path
from . import views

urlpatterns = [
    # User Routes 
    # ผู้รับผิดชอบ : ปภังกร 
    path('', views.index, name='index'), # ผู้รับผิดชอบ : ปภังกร 
    path('confirm/', views.confirm, name='confirm'), # ผู้รับผิดชอบ : ปภังกร 
    path('timer/', views.timer, name='timer'), # ผู้รับผิดชอบ : ปภังกร 
    path('feedback/', views.feedback, name='feedback'), # ผู้รับผิดชอบ : ปภังกร 



    # Admin Routes
    # ผู้รับผิดชอบ : สถาพร
    path('admin-portal/login/', views.admin_login, name='admin_login'), # ผู้รับผิดชอบ : สถาพร
    # ผู้รับผิดชอบ : ธนสิทธิ์
    path('admin-portal/monitor/', views.admin_monitor, name='admin_monitor'),  # ผู้รับผิดชอบ : ธนสิทธิ์
    # ผู้รับผิดชอบ : อัษฎาวุธ
    path('admin-portal/booking/', views.admin_booking, name='admin_booking'), # ผู้รับผิดชอบ : อัษฎาวุธ
    # ผู้รับผิดชอบ : ณัฐกรณ์
    path('admin-portal/manage-pc/', views.admin_manage_pc, name='admin_manage_pc'), # ผู้รับผิดชอบ : ณัฐกรณ์
    # ผู้รับผิดชอบ : ลลิดา
    path('admin-portal/software/', views.admin_software, name='admin_software'), # ผู้รับผิดชอบ : ลลิดา
    # ผู้รับผิดชอบ : เขมมิกา
    path('admin-portal/report/', views.admin_report, name='admin_report'), # ผู้รับผิดชอบ : เขมมิกา
    # ผู้รับผิดชอบ : ภานุวัฒน์
    path('admin-portal/config/', views.admin_config, name='admin_config'), # ผู้รับผิดชอบ : ภานุวัฒน์

    # API Routes
    path('api/monitor-data/', views.api_monitor_data, name='api_monitor_data'),
]