from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. เข้าผ่าน /kiosk/
    path('kiosk/', include('lab_management.urls')), 
    
    # 2. เพิ่มบรรทัดนี้: ทำให้เข้าผ่านหน้าแรกสุด (Path ว่าง) ได้ด้วย
    path('', include('lab_management.urls')), 
]