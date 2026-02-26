from .auth import LoginView, LogoutView
from .kiosk import IndexView, CheckinView, CheckoutView, StatusView, FeedbackView, VerifyUserAPIView
from .monitor import AdminMonitorView, AdminMonitorDataAPIView, AdminCheckinView, AdminCheckoutView
from .booking import AdminBookingView, AdminBookingDetailView, AdminImportBookingView, AdminBookingDataAPIView, AdminBookingAddAPIView, AdminBookingStatusAPIView
from .manage_pc import AdminManagePcView, AdminAddPcView, AdminManagePcEditView, AdminManagePcDeleteView
from .software import AdminSoftwareView, AdminSoftwareEditView, AdminSoftwareDeleteView
from .report import AdminReportView, AdminReportAPIView, AdminReportExportView
from .config import AdminConfigView, AdminUserView, AdminUserEditView, AdminUserDeleteView
