from django.urls import path
from . import views

urlpatterns = [
    # Kiosk (no login required)
    path('', views.IndexView.as_view(), name='index'),
    path('api/verify-user/', views.VerifyUserAPIView.as_view(), name='verify_user_api'),
    path('checkin/<str:pc_id>/', views.CheckinView.as_view(), name='checkin'),
    path('checkout/<str:pc_id>/', views.CheckoutView.as_view(), name='checkout'),
    path('status/<str:pc_id>/', views.StatusView.as_view(), name='status'),
    path('feedback/<str:pc_id>/<int:software_id>/', views.FeedbackView.as_view(), name='feedback'),

    # Auth
    path('admin-portal/login/', views.LoginView.as_view(), name='admin_login'),
    path('admin-portal/logout/', views.LogoutView.as_view(), name='admin_logout'),

    # Admin User Management
    path('admin-portal/users/', views.AdminUserView.as_view(), name='admin_users'),
    path('admin-portal/users/<int:pk>/edit/', views.AdminUserEditView.as_view(), name='admin_user_edit'),
    path('admin-portal/users/<int:pk>/delete/', views.AdminUserDeleteView.as_view(), name='admin_user_delete'),

    # Admin Monitor
    path('admin-portal/monitor/', views.AdminMonitorView.as_view(), name='admin_monitor'),
    path('admin-portal/api/monitor/data/', views.AdminMonitorDataAPIView.as_view(), name='admin_monitor_data_api'),
    path('admin-portal/checkin/<str:pc_id>/', views.AdminCheckinView.as_view(), name='admin_checkin'),
    path('admin-portal/checkout/<str:pc_id>/', views.AdminCheckoutView.as_view(), name='admin_checkout'),

    # Booking
    path('admin-portal/booking/', views.AdminBookingView.as_view(), name='admin_booking'),
    path('admin-portal/booking/import/', views.AdminImportBookingView.as_view(), name='admin_booking_import'),
    path('admin-portal/booking/<int:pk>/', views.AdminBookingDetailView.as_view(), name='admin_booking_detail'),

    # Booking API (AJAX)
    path('admin-portal/api/bookings/data/', views.AdminBookingDataAPIView.as_view(), name='admin_booking_data_api'),
    path('admin-portal/api/bookings/add/', views.AdminBookingAddAPIView.as_view(), name='admin_booking_add_api'),
    path('admin-portal/api/bookings/<int:pk>/status/', views.AdminBookingStatusAPIView.as_view(), name='admin_booking_status_api'),

    # Manage PC
    path('admin-portal/manage-pc/', views.AdminManagePcView.as_view(), name='admin_manage_pc'),
    path('admin-portal/manage-pc/add/', views.AdminAddPcView.as_view(), name='admin_add_pc'),
    path('admin-portal/manage-pc/<int:pc_id>/edit/', views.AdminManagePcEditView.as_view(), name='admin_manage_pc_edit'),
    path('admin-portal/manage-pc/<int:pc_id>/delete/', views.AdminManagePcDeleteView.as_view(), name='admin_manage_pc_delete'),

    # Software
    path('admin-portal/software/', views.AdminSoftwareView.as_view(), name='admin_software'),
    path('admin-portal/software/<int:pk>/edit/', views.AdminSoftwareEditView.as_view(), name='admin_software_edit'),
    path('admin-portal/software/<int:pk>/delete/', views.AdminSoftwareDeleteView.as_view(), name='admin_software_delete'),

    # Report
    path('admin-portal/report/', views.AdminReportView.as_view(), name='admin_report'),
    path('admin-portal/report/api/logs/', views.AdminReportAPIView.as_view(), name='admin_report_api'),
    path('admin-portal/report/export/', views.AdminReportExportView.as_view(), name='admin_report_export'),

    # Config
    path('admin-portal/config/', views.AdminConfigView.as_view(), name='admin_config'),
]
