/* admin-manage-pc.js (Optimized for Django Forms Integration) */

let myModal;

document.addEventListener('DOMContentLoaded', () => {
    // 1. กำหนดค่าเริ่มต้นให้ Modal
    const modalElement = document.getElementById('pcModal');
    if (modalElement) {
        myModal = new bootstrap.Modal(modalElement);
    }

    // 2. ดักจับการกดบันทึก (Validation) 
    // ถ้าตั้งค่าเป็น AI Workstation ต้องบังคับให้เลือกโปรแกรมอย่างน้อย 1 ตัว
    const pcForm = document.getElementById('pcForm');
    if (pcForm) {
        pcForm.addEventListener('submit', function(e) {
            const pcType = document.getElementById('editPcType').value;
            const checkedRadio = document.querySelector('input[name="software_id"]:checked');
            
            if (pcType === 'AI') {
                if (!checkedRadio) {
                    e.preventDefault(); // ยกเลิกการ submit แบบฟอร์ม
                    alert('⚠️ สำหรับเครื่อง AI Workstation กรุณาเลือก Software/AI อย่างน้อย 1 รายการก่อนบันทึกครับ');
                }
            }
        });
    }
});

// 3. ฟังก์ชันควบคุมสถานะของกล่องเลือก Software
function refreshSoftwareState() {
    const pcType = document.getElementById('editPcType').value;
    const radios = document.querySelectorAll('input[name="software_id"]');
    
    radios.forEach(radio => {
        const card = radio.closest('.soft-card');
        if (!card) return;

        // กฎ: 
        // - ถ้าเป็น General (ใช้งานทั่วไป) ให้ล็อคกล่องทุกตัว ไม่ให้คลิกได้
        // - ถ้าเป็น AI ให้ "ไม่ล็อค" ปล่อยให้คลิกเลือกได้
        let isLocked = (pcType === 'General');

        if (isLocked) {
            card.classList.add('locked');
            card.classList.remove('active');
            radio.checked = false; // ยกเลิกการเลือกทันที
        } else {
            card.classList.remove('locked'); // ปลดล็อคทั้งหมด
        }
    });
}

// 4. ฟังก์ชันสำหรับการคลิกเลือกกล่อง Software
function selectCard(element) {
    if (element.classList.contains('locked')) return; 

    // ล้างสถานะ active ของการ์ดใบอื่นทั้งหมด (เพราะเราให้เลือกได้แค่ 1 ตัว)
    document.querySelectorAll('.soft-card').forEach(card => card.classList.remove('active'));
    
    // ตั้งให้ใบที่เพิ่งคลิกเป็น active
    element.classList.add('active');
    
    // ติ๊ก Radio button ที่ซ่อนอยู่ด้านในให้เป็น true
    const radio = element.querySelector('input[type="radio"]');
    if(radio) radio.checked = true;
}

// 5. ฟังก์ชันเปิด Modal สำหรับการ "เพิ่มเครื่องใหม่"
function openAddModal() {
    // ปรับชื่อ Header และ Action URL ของฟอร์มให้พุ่งไปที่ view สำหรับสร้างเครื่องใหม่
    document.getElementById('modalHeaderTitle').innerHTML = '<i class="bi bi-pc-display me-2"></i>เพิ่มเครื่องใหม่';
    document.getElementById('pcForm').action = "/admin-portal/manage-pc/add/"; 
    
    // ล้างค่าเก่าในกล่อง Input
    document.getElementById('editPcName').value = '';
    document.getElementById('editPcStatus').value = 'AVAILABLE';
    document.getElementById('editPcType').value = 'General';
    
    // ล้างการเลือกซอฟต์แวร์
    document.querySelectorAll('.soft-card').forEach(card => card.classList.remove('active'));
    document.querySelectorAll('input[name="software_id"]').forEach(radio => radio.checked = false);
    
    refreshSoftwareState();
    
    if(myModal) myModal.show();
}

// 6. ฟังก์ชันเปิด Modal สำหรับการ "แก้ไขข้อมูลเครื่อง"
function openEditModal(id, name, status, softwareId, softwareType) {
    // ปรับชื่อ Header และ Action URL ให้ส่ง ID เข้าไปแก้
    document.getElementById('modalHeaderTitle').innerHTML = '<i class="bi bi-pencil-square me-2"></i>แก้ไขข้อมูลเครื่อง: ' + name;
    document.getElementById('pcForm').action = `/admin-portal/manage-pc/${id}/edit/`; 
    
    // ใส่ค่าเดิมของเครื่อง
    document.getElementById('editPcName').value = name;
    document.getElementById('editPcStatus').value = status;
    
    // เซ็ต Dropdown ประเภทเครื่องให้เป็น AI ทันทีถ้ามีซอฟต์แวร์ผูกอยู่
    document.getElementById('editPcType').value = softwareId ? 'AI' : 'General';
    
    // ล้างการเลือกเก่าทิ้งทั้งหมด
    document.querySelectorAll('.soft-card').forEach(card => card.classList.remove('active'));
    document.querySelectorAll('input[name="software_id"]').forEach(radio => radio.checked = false);
    
    // อัปเดตสถานะการล็อค
    refreshSoftwareState();
    
    // ถ้ามี Software อยู่แล้ว ให้ทำการคลิกเลือกกล่องนั้นอัตโนมัติ
    if (softwareId) {
        let radio = document.getElementById(`sw_${softwareId}`);
        if(radio) {
            radio.checked = true;
            radio.closest('.soft-card').classList.add('active'); 
        }
    }
    
    if(myModal) myModal.show();
}