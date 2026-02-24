/* admin-booking.js (Django Integration Version) */

// ==========================================
// 1. UTILITIES & SETUP
// ==========================================

// ฟังก์ชันสำหรับดึง CSRF Token 
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------------------------------------
    // 🌟 FEATURE: USER LOOKUP (ตรวจสอบชื่ออัตโนมัติตอนพิมพ์รหัส)
    // ---------------------------------------------------------
    const studentInput = document.getElementById('id_student_id'); // ดึง ID มาจาก Django Form
    
    if (studentInput) {
        // สร้างพื้นที่สำหรับแสดงชื่อใต้ช่องกรอก
        const hintEl = document.createElement('div');
        hintEl.id = 'userLookupHint';
        hintEl.className = 'form-text mt-1 small';
        studentInput.parentNode.appendChild(hintEl);

        studentInput.addEventListener('change', async (e) => {
            const id = e.target.value.trim();
            if (!id) { hintEl.innerHTML = ''; return; }
            
            hintEl.innerHTML = '<span class="text-muted"><i class="spinner-border spinner-border-sm" style="width: 1rem; height: 1rem;"></i> กำลังตรวจสอบข้อมูล...</span>';
            
            try {
                // ยิงไปที่ API Verify User ที่เราทำไว้ในหน้า Kiosk
                const response = await fetch('/api/verify-user/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ student_id: id })
                });

                const result = await response.json();

                if (response.ok && result.status === 'success') {
                    const roleName = result.data.role === 'staff' ? 'บุคลากร' : 'นักศึกษา';
                    hintEl.innerHTML = `<span class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i>${result.data.name} (${roleName})</span>`;
                } else {
                    hintEl.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-circle-fill me-1"></i>ไม่พบข้อมูลในระบบ หรือรหัสผิด</span>`;
                }
            } catch (error) {
                console.error(error);
                hintEl.innerHTML = `<span class="text-warning"><i class="bi bi-wifi-off me-1"></i>ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้</span>`;
            }
        });
    }
});

// ==========================================
// 2. QUICK ACTIONS (จัดการสถานะในตาราง)
// ==========================================

// เปลี่ยนสถานะ (Approve / Reject) แบบไม่ต้องโหลดหน้าใหม่
async function updateBookingStatus(bookingId, newStatus) {
    if (newStatus === 'REJECTED' && !confirm("ยืนยันการปฏิเสธ/ยกเลิก รายการจองนี้?")) return;
    if (newStatus === 'APPROVED' && !confirm("ยืนยันการอนุมัติ รายการจองนี้?")) return;

    try {
        // (รอสร้าง View สำหรับ API นี้ใน Django)
        const response = await fetch(`/admin-portal/booking/${bookingId}/update-status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            location.reload(); // รีเฟรชหน้าเพื่อแสดงผลใหม่
        } else {
            alert('เกิดข้อผิดพลาดในการอัปเดตสถานะ');
        }
    } catch (error) {
        console.error(error);
        alert('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
    }
}

// ลบข้อมูลการจอง
async function deleteBookingRecord(bookingId) {
    if (!confirm("ยืนยันการลบข้อมูลการจองนี้? (ไม่สามารถกู้คืนได้)")) return;

    try {
        // (รอสร้าง View สำหรับ API นี้ใน Django)
        const response = await fetch(`/admin-portal/booking/${bookingId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            location.reload(); 
        } else {
            alert('เกิดข้อผิดพลาดในการลบข้อมูล');
        }
    } catch (error) {
        console.error(error);
        alert('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
    }
}

// ==========================================
// 3. IMPORT / TEMPLATE LOGIC
// ==========================================

function downloadCSVTemplate() {
    const headers = [
        "รหัสผู้ใช้งาน", "ชื่อ-สกุล", "สถานะ", "เบอร์โทร", "อีเมล", 
        "เครื่องที่ใช้ (PC)", "Software / AI ที่จอง", "วันที่ใช้บริการ", 
        "ช่วงเวลาใช้บริการ", "รหัสคณะ/สำนัก"
    ];

    const sampleRows = [
        ["66123456", "นายสมชาย ตัวอย่าง", "นักศึกษา", "081-123-4567", "-", "PC-01", "VS Code", "17/01/2026", "09:00-10:30", "EN"],
        ["guest001", "นางสมหญิง ทดสอบ", "บุคคลภายนอก", "-", "-", "PC-05", "ChatGPT Plus + Midjourney", "17/01/2026", "13:00-15:00", "-"]
    ];

    let csvContent = "\uFEFF" + headers.join(",") + "\n";
    sampleRows.forEach(row => {
        const safeRow = row.map(cell => cell.includes(',') ? `"${cell}"` : cell);
        csvContent += safeRow.join(",") + "\n";
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.setAttribute("href", url);
    link.setAttribute("download", "booking_template.csv");
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ส่งไฟล์ไป Import ที่ Django (เหมือนหน้า Report)
async function handleImport(input) {
    const file = input.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('csv_file', file);
    
    try {
        const response = await fetch('/admin-portal/booking/import/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            if (result.status === 'success') {
                alert(`✅ นำเข้าข้อมูลสำเร็จ!\nเพิ่มรายการจอง: ${result.imported_count} รายการ`);
                location.reload();
            } else {
                alert(`❌ เกิดข้อผิดพลาด: ${result.message}`);
            }
        } else {
            alert("❌ เซิร์ฟเวอร์ไม่สามารถประมวลผลไฟล์ได้");
        }
    } catch (err) {
        console.error(err);
        alert("❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้");
    }

    input.value = '';
}