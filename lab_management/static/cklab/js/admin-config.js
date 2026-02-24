// lab_management/static/cklab/js/admin-config.js

document.addEventListener('DOMContentLoaded', function() {
    
    // --------------------------------------------------------
    // 1. จัดการ Switch เปิด-ปิด ห้อง (Event Listener)
    // --------------------------------------------------------
    const switchBtn = document.getElementById('labStatusSwitch');
    
    // เรียกฟังก์ชัน 1 ครั้งตอนโหลดหน้า เพื่อปรับสีให้ตรงกับค่าปัจจุบัน
    updateLabStatusUI(); 

    // ดักจับการกดเปลี่ยนค่า (Change Event)
    if (switchBtn) {
        switchBtn.addEventListener('change', function() {
            updateLabStatusUI();
        });
    }

    // --------------------------------------------------------
    // 2. ล้างฟอร์มเมื่อปิด Modal
    // --------------------------------------------------------
    const adminModal = document.getElementById('adminModal');
    if (adminModal) {
        adminModal.addEventListener('hidden.bs.modal', function () {
            const form = adminModal.querySelector('form');
            if (form) {
                form.reset();
            }
        });
    }

    // --------------------------------------------------------
    // 3. ตั้งเวลาปิด Alert อัตโนมัติ (5 วินาที)
    // --------------------------------------------------------
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // ตรวจสอบว่ามี Bootstrap script โหลดอยู่จริงไหมป้องกัน Error
            if (typeof bootstrap !== 'undefined') {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                // ถ้าไม่มี Bootstrap JS ให้ซ่อนด้วย CSS ธรรมดา
                alert.style.display = 'none';
            }
        }, 5000);
    });
});

// ฟังก์ชันอัปเดต UI (ย้ายเข้ามาข้างใน หรือไว้ข้างนอกก็ได้ แต่ไว้ข้างนอกจะเรียกใช้ง่ายกว่าถ้ามี Inline Script)
function updateLabStatusUI() {
    const switchBtn = document.getElementById('labStatusSwitch');
    const label = document.getElementById('labStatusLabel');
    
    if (!switchBtn || !label) return;

    if (switchBtn.checked) {
        label.textContent = 'เปิดให้บริการ (Open)';
        label.classList.remove('text-danger');
        label.classList.add('text-success');
    } else {
        label.textContent = 'ปิดให้บริการ (Closed)';
        label.classList.remove('text-success');
        label.classList.add('text-danger');
    }
}