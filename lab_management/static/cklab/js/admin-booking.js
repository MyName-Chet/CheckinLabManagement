// --- admin-booking.js (Django API Version - Real Database) ---

let bookingModal;
let allPCs = [];
let allBookings = [];
let allSoftware = [];

// ==========================================
// 0. INIT & HELPERS
// ==========================================

function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    if (!cookieValue) {
        cookieValue = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', async () => {
    const modalEl = document.getElementById('bookingModal');
    if (modalEl) bookingModal = new bootstrap.Modal(modalEl);

    const dateFilter = document.getElementById('bookingDateFilter');
    if (dateFilter) {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        dateFilter.value = `${yyyy}-${mm}-${dd}`;
    }

    // โหลดข้อมูลเริ่มต้นจาก Backend
    await fetchBookingData();

    // Event Listeners สำหรับ Modal
    document.getElementById('bkDate')?.addEventListener('change', filterPCList);
    document.getElementById('bkTimeSlot')?.addEventListener('change', filterPCList);
    document.getElementById('bkTypeSelect')?.addEventListener('change', () => {
        toggleSoftwareList();
        filterPCList();
    });

    // Event Listener: ค้นหาชื่อผู้จองอัตโนมัติ
    const userInput = document.getElementById('bkUser');
    if (userInput) {
        if (!document.getElementById('userLookupHint')) {
            const hint = document.createElement('div');
            hint.id = 'userLookupHint';
            hint.className = 'form-text mt-1';
            userInput.parentNode.appendChild(hint);
        }
        userInput.addEventListener('change', checkUserLookup);
    }
});

// ==========================================
// 1. DATA FETCHING (API)
// ==========================================

async function fetchBookingData() {
    try {
        // ยิงไปขอข้อมูลการจอง, เครื่อง PC, และ Software ทั้งหมดจาก Backend
        const response = await fetch('/kiosk/admin-portal/api/bookings/data/', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        
        if (!response.ok) throw new Error('Failed to fetch data');
        
        const data = await response.json();
        if (data.status === 'success') {
            allPCs = data.pcs || [];
            allBookings = data.bookings || [];
            allSoftware = data.software || [];
            
            initFormOptions();
            renderBookings();
        }
    } catch (error) {
        console.error("Error fetching booking data:", error);
    }
}

function initFormOptions() {
    const swFilter = document.getElementById('bkSoftwareFilter');
    if (swFilter) {
        swFilter.innerHTML = '<option value="">-- ไม่ระบุ (แสดงทั้งหมด) --</option>';
        if (allSoftware.length > 0) {
            allSoftware.forEach(sw => {
                swFilter.innerHTML += `<option value="${sw.name}">${sw.name}</option>`;
            });
            swFilter.disabled = false;
        } else {
            swFilter.innerHTML = '<option value="">(ไม่พบข้อมูล Software)</option>';
            swFilter.disabled = true;
        }
    }
}

// ==========================================
// 2. FEATURE: USER LOOKUP
// ==========================================

async function checkUserLookup() {
    const input = document.getElementById('bkUser');
    const hint = document.getElementById('userLookupHint');
    const val = input.value.trim();

    if (!val) {
        hint.innerHTML = '';
        return;
    }

    hint.innerHTML = '<span class="text-muted"><span class="spinner-border spinner-border-sm"></span> กำลังค้นหา...</span>';

    try {
        // ใช้ API ตรวจสอบนักศึกษาตัวเดียวกับที่ใช้อยู่ในระบบ
        const response = await fetch('/kiosk/api/verify-user/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify({ student_id: val })
        });
        
        const data = await response.json();

        if (data.status === 'success') {
            const roleTxt = data.data.role === 'student' ? 'นักศึกษา' : 'บุคลากร';
            hint.innerHTML = `<span class="text-success fw-bold"><i class="bi bi-check-circle-fill"></i> พบข้อมูล: ${data.data.name} (${roleTxt})</span>`;
            hint.dataset.verifiedName = data.data.name; // เก็บชื่อไว้ใช้ตอนเซฟ
        } else {
            hint.innerHTML = `<span class="text-warning"><i class="bi bi-exclamation-circle"></i> ไม่พบข้อมูลในระบบ (ระบบจะบันทึกเป็นชื่อ Guest แทน)</span>`;
            hint.dataset.verifiedName = '';
        }
    } catch (error) {
        hint.innerHTML = `<span class="text-danger"><i class="bi bi-x-circle"></i> ระบบเครือข่ายมีปัญหา</span>`;
    }
}

// ==========================================
// 3. FEATURE: FILTER PC & RENDER
// ==========================================

function filterPCList() {
    const pcSelect = document.getElementById('bkPcSelect');
    if (!pcSelect) return;

    const swName = document.getElementById('bkSoftwareFilter').value.toLowerCase();
    const selDate = document.getElementById('bkDate').value;
    const selTimeSlot = document.getElementById('bkTimeSlot').value;
    const selType = document.getElementById('bkTypeSelect').value; 

    if (!selDate || !selTimeSlot) {
        pcSelect.innerHTML = '<option value="">-- กรุณาเลือกวันและเวลาก่อน --</option>';
        return;
    }

    const [selStart, selEnd] = selTimeSlot.split('-');
    const currentValue = pcSelect.value;
    pcSelect.innerHTML = '<option value="">-- เลือกเครื่อง --</option>';
    let count = 0;

    allPCs.forEach(pc => {
        // --- A. กรอง Type (General / AI) ---
        const isAI = pc.software_type === 'AI';
        if (selType === 'General' && isAI) return;
        if (selType === 'AI' && !isAI) return;

        // --- B. กรอง Software Filter ---
        if (swName !== "" && pc.software_name.toLowerCase() !== swName) return;

        // --- C. เช็คสถานะซ่อม ---
        if (pc.status === 'MAINTENANCE') {
            pcSelect.innerHTML += `<option value="${pc.id}" disabled style="color: #6c757d;">🔴 ${pc.name} (แจ้งซ่อม)</option>`;
            count++;
            return;
        }

        // --- D. เช็คคิวว่าง (Conflict Check) ---
        const isConflict = allBookings.some(b => {
            if (String(b.pc_name) !== String(pc.name)) return false;
            if (b.date !== selDate) return false;
            if (b.status === 'REJECTED' || b.status === 'COMPLETED') return false;
            // เช็คเวลาชน
            return (selStart < b.end_time && selEnd > b.start_time);
        });

        if (isConflict) {
            pcSelect.innerHTML += `<option value="${pc.id}" disabled style="color: #dc3545;">❌ ${pc.name} (ไม่ว่าง - จองแล้ว)</option>`;
        } else {
            const selected = (String(pc.id) === String(currentValue)) ? 'selected' : '';
            pcSelect.innerHTML += `<option value="${pc.id}" ${selected} style="color: #198754;">🟢 ${pc.name} (ว่าง)</option>`;
        }
        count++;
    });

    if (count === 0) {
        pcSelect.innerHTML = `<option value="" disabled>❌ ไม่พบเครื่องที่ตรงตามเงื่อนไข</option>`;
    }

    updateSoftwareList();
}

function updateSoftwareList() {
    const pcId = document.getElementById('bkPcSelect').value;
    const container = document.getElementById('aiCheckboxList');
    const hint = document.getElementById('pcSoftwareHint');

    if (hint) hint.innerText = "";
    if (!container) return;
    container.innerHTML = '';

    if (!pcId) {
        container.innerHTML = '<span class="text-muted small fst-italic">กรุณาเลือกเครื่องก่อน...</span>';
        return;
    }

    const pc = allPCs.find(p => String(p.id) === String(pcId));
    if (pc && pc.software_name && pc.software_name !== '-') {
        // ให้เลือกโปรแกรมที่มีในเครื่องนั้นแบบบังคับเลือก 1 อัน
        container.innerHTML = `
            <div class="form-check form-check-inline mb-1">
                <input class="form-check-input" type="checkbox" id="sw_chk_0" value="${pc.software_name}" checked disabled>
                <label class="form-check-label small" for="sw_chk_0">${pc.software_name}</label>
            </div>
            <input type="hidden" name="selected_software" value="${pc.software_name}">
        `;
    } else {
        container.innerHTML = '<span class="text-muted small">- ไม่พบรายการ Software พิเศษในเครื่องนี้ -</span>';
    }
}

function toggleSoftwareList() {
    const type = document.getElementById('bkTypeSelect').value;
    const box = document.getElementById('aiSelectionBox');
    if (box) {
        if (type === 'AI') box.classList.remove('d-none');
        else box.classList.add('d-none');
    }
}

// ==========================================
// 4. RENDER TABLE
// ==========================================

function renderBookings() {
    const tbody = document.getElementById('bookingTableBody');
    if (!tbody) return;

    const filterDate = document.getElementById('bookingDateFilter').value;
    const filterStatus = document.getElementById('bookingStatusFilter').value;

    tbody.innerHTML = '';

    const filtered = allBookings.filter(b => {
        if (filterDate && b.date !== filterDate) return false;
        if (filterStatus !== 'all' && b.status.toLowerCase() !== filterStatus.toLowerCase()) return false;
        return true;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-5">ไม่มีรายการจองในช่วงเวลานี้</td></tr>`;
        return;
    }

    filtered.forEach(b => {
        let badgeClass = '', statusText = '', actionBtns = '';

        switch (b.status) {
            case 'APPROVED':
                badgeClass = 'bg-warning text-dark border border-warning';
                statusText = '🟡 จองแล้ว (Booked)';
                actionBtns = `
                    <button class="btn btn-sm btn-outline-danger" onclick="updateStatus(${b.id}, 'REJECTED')" title="ยกเลิกการจอง">
                        <i class="bi bi-x-lg"></i> ยกเลิก
                    </button>
                `;
                break;
            case 'COMPLETED':
                badgeClass = 'bg-success'; statusText = '🟢 ใช้งานเสร็จสิ้น'; break;
            case 'REJECTED':
                badgeClass = 'bg-danger bg-opacity-75'; statusText = '❌ ยกเลิกแล้ว'; break;
            default:
                badgeClass = 'bg-secondary'; statusText = b.status; break;
        }

        let softwareDisplay = '-';
        if (b.software) {
            softwareDisplay = `<span class="badge bg-primary bg-opacity-10 text-primary border border-primary"><i class="bi bi-robot me-1"></i>${b.software}</span>`;
        } else {
            softwareDisplay = '<span class="badge bg-light text-secondary border">ทั่วไป</span>';
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="ps-4 fw-bold text-dark">${formatDate(b.date)}</td>
            <td class="text-primary fw-bold">${b.start_time} - ${b.end_time}</td>
            <td>
                <div class="fw-bold text-dark">${b.user_name}</div>
                <div class="small text-muted" style="font-size: 0.75rem;">${b.user_id}</div>
            </td>
            <td><span class="badge bg-light text-dark border border-secondary">${b.pc_name}</span></td>
            <td>${softwareDisplay}</td>
            <td><span class="badge ${badgeClass}">${statusText}</span></td>
            <td class="text-end pe-4">${actionBtns}</td>
        `;
        tbody.appendChild(tr);
    });
}

function formatDate(dateStr) {
    if (!dateStr) return "-";
    const parts = dateStr.split('-');
    if (parts.length !== 3) return dateStr;
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
}

// ==========================================
// 5. CRUD OPERATIONS (CREATE / UPDATE)
// ==========================================

function openBookingModal() {
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('bkDate');
    if (dateInput) dateInput.value = today;

    if (document.getElementById('bkPcSelect')) document.getElementById('bkPcSelect').value = '';
    if (document.getElementById('bkTimeSlot')) document.getElementById('bkTimeSlot').value = '09:00-10:30';

    const userInput = document.getElementById('bkUser');
    if (userInput) userInput.value = '';
    
    const hint = document.getElementById('userLookupHint');
    if (hint) { hint.innerHTML = ''; hint.dataset.verifiedName = ''; }

    if (document.getElementById('bkTypeSelect')) document.getElementById('bkTypeSelect').value = 'General';
    if (document.getElementById('bkSoftwareFilter')) document.getElementById('bkSoftwareFilter').value = '';

    filterPCList();
    toggleSoftwareList();

    if (bookingModal) bookingModal.show();
}

async function saveBooking() {
    const pcSelect = document.getElementById('bkPcSelect');
    // ดึงชื่อ PC เช่น จาก Option "🟢 PC-01 (ว่าง)" ให้เหลือแค่ "PC-01"
    const pcName = pcSelect.options[pcSelect.selectedIndex].text.split(' ')[1]; 

    const date = document.getElementById('bkDate').value;
    const timeSlotStr = document.getElementById('bkTimeSlot').value;
    const userId = document.getElementById('bkUser').value.trim();
    
    // ดึงชื่อที่ Verify มาแล้ว ถ้าไม่มีให้ใช้ UserID
    const hint = document.getElementById('userLookupHint');
    const userName = (hint && hint.dataset.verifiedName) ? hint.dataset.verifiedName : userId;

    if (!pcSelect.value || !date || !timeSlotStr || !userId) {
        alert("กรุณากรอกข้อมูลและเลือกเครื่องให้ครบถ้วน");
        return;
    }

    const [start, end] = timeSlotStr.split('-');

    const payload = {
        user_id: userId,
        user_name: userName,
        pc_name: pcName,
        date: date,
        start_time: start,
        end_time: end
    };

    try {
        const response = await fetch('/kiosk/admin-portal/api/bookings/add/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        
        if (result.status === 'success') {
            alert("บันทึกการจองเรียบร้อย");
            if (bookingModal) bookingModal.hide();
            fetchBookingData(); // รีเฟรชข้อมูลตาราง
        } else {
            alert(`ข้อผิดพลาด: ${result.message}`);
        }
    } catch (error) {
        alert("ไม่สามารถบันทึกข้อมูลได้ กรุณาลองใหม่");
    }
}

async function updateStatus(bookingId, newStatus) {
    if (newStatus === 'REJECTED' && !confirm("ยืนยันการยกเลิกรายการจองนี้?")) return;

    try {
        const response = await fetch(`/kiosk/admin-portal/api/bookings/${bookingId}/status/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify({ status: newStatus })
        });

        const result = await response.json();
        if (result.status === 'success') {
            fetchBookingData(); // รีเฟรชตาราง
        } else {
            alert(`ข้อผิดพลาด: ${result.message}`);
        }
    } catch (error) {
        alert("อัปเดตสถานะไม่สำเร็จ");
    }
}

// ==========================================
// 6. CSV TEMPLATE DOWNLOAD
// ==========================================

function downloadCSVTemplate() {
    const headers = [
        "user_id",
        "user_name",
        "pc_name",
        "date",
        "start_time",
        "end_time"
    ];

    const sampleRows = [
        ["66123456", "นายสมชาย ตัวอย่าง", "PC-01", "2026-03-01", "09:00", "10:30"],
        ["guest001", "นางสมหญิง ทดสอบ", "PC-05", "2026-03-01", "13:30", "15:00"]
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
    link.setAttribute("download", "booking_import_template.csv");
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}