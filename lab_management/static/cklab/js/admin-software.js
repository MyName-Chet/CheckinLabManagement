/* admin-software.js (Django Version - UI & Search Only) */

let softwareModal;

document.addEventListener('DOMContentLoaded', () => {
    // 1. Init Modal สำหรับหน้าเพิ่มรายการ
    const modalEl = document.getElementById('softwareModal');
    if (modalEl) {
        softwareModal = new bootstrap.Modal(modalEl);
    }

    // 2. ระบบค้นหา (Client-side Search Filter)
    const searchInput = document.getElementById('softwareSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const filterValue = this.value.toLowerCase(); // ข้อความที่พิมพ์ค้นหา
            const tableRows = document.querySelectorAll('tbody tr'); // ดึงแถวในตารางทั้งหมด

            tableRows.forEach(row => {
                // ข้ามแถวที่แสดงข้อความ "ยังไม่มีข้อมูล" (เช็คจาก attribute colspan)
                if (row.querySelector('td[colspan]')) return;

                // ดึงข้อความในแถวนั้นๆ มาเช็ค (ครอบคลุมทั้ง ชื่อ, แพ็กเกจ, และประเภท)
                const rowText = row.textContent.toLowerCase();
                
                // ถ้าข้อความในแถว มีคำที่ค้นหา ให้แสดงแถวนั้นไว้ ถ้าไม่มีให้ซ่อน
                if (rowText.includes(filterValue)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});

// ==========================================
// 🎨 UI Management
// ==========================================

// ฟังก์ชันเปิด Modal สำหรับเพิ่มรายการใหม่
function openModal() {
    if (softwareModal) {
        // รีเซ็ตฟอร์มให้กลับเป็นค่าเริ่มต้น (เผื่อผู้ใช้พิมพ์ค้างไว้แล้วกดปิด)
        const form = document.querySelector('#softwareModal form');
        if(form) form.reset();
        
        // รีเซ็ตตัวเลือกกลับเป็น 'Software'
        selectType('Software', document.querySelectorAll('.software-type-card')[0]);
        
        softwareModal.show();
    }
}

// ฟังก์ชันเลือกประเภท AI / Software (สลับคลาส CSS ให้สวยงาม)
function selectType(type, element) {
    // 1. อัปเดตค่าให้ hidden input เพื่อเตรียมส่ง POST ไปให้ Django
    const editTypeInput = document.getElementById('editType');
    if (editTypeInput) {
        editTypeInput.value = type;
    }
    
    // 2. ล้างสีกรอบเก่าออกจากการ์ดทั้งหมด
    document.querySelectorAll('.software-type-card').forEach(el => {
        el.classList.remove('border-primary', 'bg-primary', 'bg-opacity-10', 'active', 'border-2');
        if (!el.classList.contains('border')) {
            el.classList.add('border'); // คืนค่าขอบสีเทาปกติ
        }
    });
    
    // 3. เติมสีน้ำเงินให้กับการ์ดที่ถูกคลิกเลือก
    if (element) {
        element.classList.remove('border');
        element.classList.add('border-primary', 'border-2', 'bg-primary', 'bg-opacity-10', 'active');
    } else {
        // กรณีเรียกใช้จากหน้า Edit (หา element จาก ID แทน)
        const targetCard = document.getElementById('card-' + type);
        if (targetCard) {
            targetCard.classList.remove('border');
            targetCard.classList.add('border-primary', 'border-2', 'bg-primary', 'bg-opacity-10', 'active');
        }
    }
}