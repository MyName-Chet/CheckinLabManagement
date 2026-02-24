from django.urls import path
from .views import kiosk, auth, monitor, manage_pc, software , report , config , booking 

urlpatterns = [
    # 1. ฝั่งผู้ใช้งาน (User / Kiosk) - ผู้รับผิดชอบ: ปภังกร
    path('', kiosk.IndexView.as_view(), name='kiosk_index'),
    path('checkin/<str:pc_id>/', kiosk.CheckinView.as_view(), name='kiosk_checkin'),
    path('checkout/<str:pc_id>/', kiosk.CheckoutView.as_view(), name='kiosk_checkout'),
    path('api/status/<str:pc_id>/', kiosk.StatusView.as_view(), name='api_status'), 
    path('api/verify-user/', kiosk.VerifyUserAPIView.as_view(), name='api_verify_user'), 
    path('feedback/<str:pc_id>/<int:software_id>/', kiosk.FeedbackView.as_view(), name='kiosk_feedback'),

    # 2. ระบบ Login + จัดการ Admin User - ผู้รับผิดชอบ: สถาพร (สำรอง โดย ภานุวัฒน์)
    path('admin-portal/login/', auth.LoginView.as_view(), name='login'), # สถาพร
    path('admin-portal/logout/', auth.LogoutView.as_view(), name='logout'), # สถาพร
    path('admin-portal/users/', auth.AdminUserView.as_view(), name='admin_user'), # สถาพร (สำรอง โดย ภานุวัฒน์)
    path('admin-portal/users/<int:pk>/edit/', auth.AdminUserEditView.as_view(), name='admin_user_edit'), # สถาพร (สำรอง โดย ภานุวัฒน์)
    path('admin-portal/users/<int:pk>/delete/', auth.AdminUserDeleteView.as_view(), name='admin_user_delete'), # สถาพร (สำรอง โดย ภานุวัฒน์)

    # 3. ฝั่งผู้ดูแลระบบ (Admin Portal)
    path('admin-portal/monitor/', monitor.AdminMonitorView.as_view(), name='admin_monitor'), # ธนสิทธิ์ (สำรอง โดย ปภังกร)
    path('admin-portal/api/monitor/data/', monitor.AdminMonitorDataAPIView.as_view(), name='api_monitor_data'),# ธนสิทธิ์ (สำรอง โดย ปภังกร)
    path('admin-portal/checkin/<str:pc_id>/', monitor.AdminCheckinView.as_view(), name='admin_checkin'), # ธนสิทธิ์ (สำรอง โดย ปภังกร)
    path('admin-portal/checkout/<str:pc_id>/', monitor.AdminCheckoutView.as_view(), name='admin_checkout'), # ธนสิทธิ์ (สำรอง โดย ปภังกร)
    
    path('admin-portal/booking/', booking.AdminBookingView.as_view(), name='admin_booking'), # อัษฎาวุธ (สำรอง โดย ลลิดา)
    path('admin-portal/booking/import/', booking.AdminImportBookingView.as_view(), name='admin_booking_import'), # อัษฎาวุธ  (สำรอง โดย ลลิดา)
    path('admin-portal/api/bookings/data/', booking.AdminBookingDataAPIView.as_view(), name='api_booking_data'),# อัษฎาวุธ  (สำรอง โดย ลลิดา)
    path('admin-portal/api/bookings/add/', booking.AdminBookingAddAPIView.as_view(), name='api_booking_add'), # อัษฎาวุธ  (สำรอง โดย ลลิดา)
    path('admin-portal/api/bookings/<int:pk>/status/', booking.AdminBookingStatusAPIView.as_view(), name='api_booking_status'), # อัษฎาวุธ  (สำรอง โดย ลลิดา)
    
    path('admin-portal/manage-pc/', manage_pc.AdminManagePcView.as_view(), name='admin_manage_pc'), # ณัฐกรณ์  (สำรอง โดย ลลิดา)
    path('admin-portal/manage-pc/add/', manage_pc.AdminAddPcView.as_view(), name='admin_add_pc'), # ณัฐกรณ์
    path('admin-portal/manage-pc/<str:pc_id>/edit/', manage_pc.AdminManagePcEditView.as_view(), name='admin_manage_pc_edit'), # ณัฐกรณ์ (สำรอง โดย ลลิดา)
    path('admin-portal/manage-pc/<str:pc_id>/delete/', manage_pc.AdminManagePcDeleteView.as_view(), name='admin_manage_pc_delete'), # ณัฐกรณ์ (สำรอง โดย ลลิดา)
    
    path('admin-portal/software/', software.AdminSoftwareView.as_view(), name='admin_software'), # ลลิดา  
    path('admin-portal/software/<int:pk>/edit/', software.AdminSoftwareEditView.as_view(), name='admin_software_edit'), # ลลิดา
    path('admin-portal/software/<int:pk>/delete/', software.AdminSoftwareDeleteView.as_view(), name='admin_software_delete'), # ลลิดา
    
    path('admin-portal/report/', report.AdminReportView.as_view(), name='admin_report'), # เขมมิกา
    path('admin-portal/report/export/', report.AdminReportExportView.as_view(), name='admin_report_export'), # เขมมิกา
    path('admin-portal/report/api/logs/', report.AdminReportAPIView.as_view(), name='admin_report_api'),
    path('admin-portal/report/import/', report.AdminReportView.as_view(), name='admin_report_import'),
    path('admin-portal/config/', config.AdminConfigView.as_view(), name='admin_config'), # ภานุวัฒน์
]