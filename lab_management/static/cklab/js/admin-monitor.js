// --- admin-monitor.js (Complete Version: Real-time Monitor & Future Bookings) ---

let checkInModal, manageActiveModal;
let currentTab = 'internal';
let verifiedUserData = null;
let currentFilter = 'all'; 

// ฟังก์ชันสำหรับดึง CSRF Token
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

document.addEventListener('DOMContentLoaded', () => {
    const modalEl = document.getElementById('checkInModal');
    if (modalEl) checkInModal = new bootstrap.Modal(modalEl);
    
    const manageEl = document.getElementById('manageActiveModal');
    if (manageEl) manageActiveModal = new bootstrap.Modal(manageEl);

    // รันครั้งแรกทันที
    renderMonitor();

    // ตั้งเวลาอัปเดตทุก 5 วินาที
    setInterval(() => {
        const isCheckinOpen = modalEl && modalEl.classList.contains('show');
        const isManageOpen = manageEl && manageEl.classList.contains('show');
        // อัปเดตเฉพาะตอนที่ไม่ได้เปิด Modal ค้างไว้ เพื่อป้องกัน UI กระตุกขณะพิมพ์
        if (!isCheckinOpen && !isManageOpen) {
            // ตรวจสอบว่าขณะนี้ผู้ใช้อยู่ที่แท็บ "คิวจอง" หรือไม่
            const isBookingTabActive = document.getElementById('panel-booking')?.classList.contains('active');
            renderMonitor({ skipBookingTable: isBookingTabActive });
        }
    }, 5000);
});

// ==========================================
// 🖥️ Render Monitor Grid & Future Bookings
// ==========================================

async function renderMonitor({ skipBookingTable = false } = {}) {
    const grid = document.getElementById('monitorGrid');
    if(!grid) return;

    try {
        const response = await fetch('/kiosk/admin-portal/api/monitor/data/', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        if (!response.ok) return;
        const data = await response.json();

        // 1. อัปเดตตัวเลขสถิติด้านบน
        updateMonitorStats(data.counts || {});

        // 2. จัดการข้อมูล Grid เครื่องคอมพิวเตอร์
        const allPcs = data.pcs || [];
        let displayPcs = allPcs;
        if (currentFilter !== 'all') {
            displayPcs = displayPcs.filter(pc => pc.status === currentFilter);
        }

        if (displayPcs.length === 0) {
            const empty = `<div class="col-12 text-center text-muted py-5 fw-bold"><i class="bi bi-inbox fs-1 d-block mb-2 text-secondary opacity-50"></i>ไม่พบข้อมูลเครื่องคอมพิวเตอร์</div>`;
            if (grid.innerHTML !== empty) grid.innerHTML = empty;
        } else {
            // DOM Diffing: อัปเดตเฉพาะ card ที่เปลี่ยนแปลง ไม่ล้าง DOM ทั้งหมด
            diffPcGrid(grid, displayPcs);
        }

        // 3. จัดการข้อมูลตารางคิวจองล่วงหน้า (แท็บที่ 2)
        // ข้ามการ re-render ตารางถ้าผู้ใช้กำลังดูแท็บ Booking อยู่ เพื่อป้องกัน UI กระพริบ
        if (!skipBookingTable) {
            renderFutureBookings(data.bookings || []);
        }

    } catch (error) {
        console.error("Error fetching monitor data:", error);
    }
}

// คืนค่า true ถ้า booking จะเริ่มภายในอีก `minutes` นาทีนับจากขณะนี้
function isBookingSoon(isoString, minutes = 30) {
    if (!isoString) return false;
    const bookingTime = new Date(isoString).getTime();
    const now = Date.now();
    return bookingTime > now && bookingTime - now <= minutes * 60 * 1000;
}

// DOM Diffing: เปรียบเทียบ card ที่มีกับข้อมูลใหม่ อัปเดตเฉพาะส่วนที่เปลี่ยน
function diffPcGrid(grid, displayPcs) {
    const existingCards = {};
    grid.querySelectorAll('[data-pc-name]').forEach(el => {
        existingCards[el.dataset.pcName] = el;
    });

    const newNames = new Set(displayPcs.map(pc => pc.name));

    // ลบ card ของเครื่องที่ filter ออกไปแล้ว
    Object.keys(existingCards).forEach(name => {
        if (!newNames.has(name)) existingCards[name].remove();
    });

    displayPcs.forEach((pc, index) => {
        const newHtml = generatePcCardHtml(pc);
        const existing = existingCards[pc.name];

        if (!existing) {
            // card ใหม่ ต้องสร้าง
            const wrapper = document.createElement('div');
            wrapper.innerHTML = newHtml;
            const newCard = wrapper.firstElementChild;
            // แทรกในตำแหน่งที่ถูกต้องตาม order
            const refNode = grid.children[index] || null;
            grid.insertBefore(newCard, refNode);
        } else {
            // card มีอยู่แล้ว — ตรวจสอบเฉพาะ inner content ของ card-body
            const wrapper = document.createElement('div');
            wrapper.innerHTML = newHtml;
            const newCardBody = wrapper.querySelector('.card-body');
            const oldCardBody = existing.querySelector('.card-body');
            if (newCardBody && oldCardBody && newCardBody.innerHTML !== oldCardBody.innerHTML) {
                oldCardBody.innerHTML = newCardBody.innerHTML;
            }
            // ตรวจ border color (status เปลี่ยน)
            const newCard = wrapper.firstElementChild?.querySelector('.card');
            const oldCard = existing.querySelector('.card');
            if (newCard && oldCard && newCard.style.borderTopColor !== oldCard.style.borderTopColor) {
                oldCard.style.borderTop = newCard.style.borderTop;
            }
            // จัดลำดับให้ถูกต้อง (ถ้าเลื่อน index)
            const currentIndex = Array.from(grid.children).indexOf(existing);
            if (currentIndex !== index) {
                const refNode = grid.children[index] || null;
                grid.insertBefore(existing, refNode);
            }
        }
    });
}

// ฟังก์ชันสร้าง HTML สำหรับ Card PC แต่ละเครื่อง
function generatePcCardHtml(pc) {
    let statusClass = '', iconClass = '', label = '', actionHtml = '', userDisplay = '';

    // ตรวจสอบว่า PC ที่ว่างอยู่มีการจองที่จะมาถึงใน 30 นาทีหรือไม่
    const bookingSoon = pc.status === 'AVAILABLE' && isBookingSoon(pc.next_booking_start_iso);

    switch(pc.status) {
        case 'AVAILABLE':
            if (bookingSoon) {
                statusClass = 'text-warning'; iconClass = 'bi-clock-history'; label = 'ว่าง (มีจองใกล้มา)';
                userDisplay = `<div class="mt-1 text-warning small fw-bold"><i class="bi bi-calendar-event"></i> จองเวลา ${pc.next_booking_time}</div>`;
                actionHtml = `<button onclick="openCheckInModal('${pc.name}')" class="btn btn-outline-warning btn-sm w-100 rounded-pill mt-3"><i class="bi bi-box-arrow-in-right me-1"></i> เช็คอิน</button>`;
            } else {
                statusClass = 'text-success'; iconClass = 'bi-check-circle'; label = 'ว่าง';
                userDisplay = `<div class="mt-1 text-muted small">พร้อมใช้งาน</div>`;
                actionHtml = `<button onclick="openCheckInModal('${pc.name}')" class="btn btn-outline-success btn-sm w-100 rounded-pill mt-3"><i class="bi bi-box-arrow-in-right me-1"></i> เช็คอิน</button>`;
            }
            break;
        case 'IN_USE': 
            statusClass = 'text-danger'; iconClass = 'bi-person-workspace'; label = 'ใช้งานอยู่'; 
            userDisplay = `
                <div class="mt-1 fw-bold text-dark text-truncate" title="${pc.user_name}"><i class="bi bi-person-fill text-primary"></i> ${pc.user_name || 'ไม่ทราบชื่อ'}</div>
                <div class="small text-danger fw-bold mt-1"><i class="bi bi-clock-history"></i> ${pc.elapsed_time || '00:00:00'}</div>
            `;
            actionHtml = `<button onclick="openManageActiveModal('${pc.name}', '${pc.user_name || ''}')" class="btn btn-outline-danger btn-sm w-100 rounded-pill mt-3"><i class="bi bi-gear-fill me-1"></i> จัดการ</button>`;
            break;
        case 'RESERVED': 
            statusClass = 'text-warning'; iconClass = 'bi-bookmark-fill'; label = 'จองแล้ว'; 
            userDisplay = `<div class="mt-1 text-dark small fw-bold"><i class="bi bi-calendar-event text-warning"></i> ${pc.next_booking_time || 'รอคิว'}</div>`;
            actionHtml = `<button class="btn btn-light text-secondary border btn-sm w-100 rounded-pill mt-3" disabled>รอใช้งาน</button>`;
            break;
        default: 
            statusClass = 'text-secondary'; iconClass = 'bi-wrench-adjustable'; label = 'แจ้งซ่อม';
            userDisplay = `<div class="mt-1 text-muted small">ปิดปรับปรุง</div>`;
            actionHtml = `<button class="btn btn-light text-secondary border btn-sm w-100 rounded-pill mt-3" disabled>งดบริการ</button>`;
    }

    let softwareHtml = (pc.software && pc.software !== '-') ? 
        `<div class="mt-2"><span class="badge ${pc.is_ai ? 'bg-primary bg-opacity-10 text-primary border-primary' : 'bg-light text-dark border-secondary'} border" style="font-size: 0.75rem; font-weight: 500;">${pc.is_ai ? '<i class="bi bi-robot"></i> ' : ''}${pc.software}</span></div>` : 
        '<div class="mt-2" style="height: 24px;"></div>';

    return `
        <div class="col-6 col-md-4 col-lg-3" data-pc-name="${pc.name}">
            <div class="card h-100 shadow-sm position-relative" style="border-top: 4px solid var(--bs-${statusClass.split('-')[1]}); border-radius: 12px;">
                <div class="card-body text-center p-3 d-flex flex-column">
                    <i class="bi ${iconClass} display-6 ${statusClass} mb-2"></i>
                    <h5 class="fw-bold mb-0 text-dark">${pc.name}</h5>
                    <div class="badge bg-light text-dark border mb-2 align-self-center mt-1">${label}</div>
                    <div class="bg-light rounded p-2 flex-grow-1 d-flex flex-column justify-content-center">
                        ${userDisplay}
                    </div>
                    ${softwareHtml}
                    ${actionHtml}
                </div>
            </div>
        </div>`;
}

// ฟังก์ชันเขียนตารางคิวจองล่วงหน้า (New Feature)
function renderFutureBookings(bookings) {
    const bookingTableBody = document.getElementById('futureBookingTableBody');
    if (!bookingTableBody) return;

    const newHtml = bookings.length === 0
        ? `<tr><td colspan="5" class="text-center py-5 text-muted"><i class="bi bi-calendar-x d-block fs-2 opacity-50 mb-2"></i>ไม่พบข้อมูลคิวจองล่วงหน้า</td></tr>`
        : bookings.map(b => `
        <tr>
            <td class="ps-4">${b.date}</td>
            <td class="text-primary fw-bold">${b.time}</td>
            <td><span class="badge bg-light text-dark border border-secondary">${b.pc_name}</span></td>
            <td>
                <div class="fw-bold">${b.user_id}</div>
            </td>
            <td><span class="badge bg-warning text-dark border border-warning bg-opacity-25">อนุมัติแล้ว</span></td>
        </tr>
    `).join('');

    if (bookingTableBody.innerHTML !== newHtml) {
        bookingTableBody.innerHTML = newHtml;
    }
}

function updateMonitorStats(counts) {
    const setVal = (id, val) => {
        const el = document.getElementById(id);
        if(el && el.innerText !== String(val)) {
            el.innerText = val || 0;
            el.style.transition = 'transform 0.2s';
            el.style.transform = 'scale(1.2)';
            setTimeout(() => el.style.transform = 'scale(1)', 200);
        }
    };
    setVal('count-available', counts.AVAILABLE || 0);
    setVal('count-in_use', counts.IN_USE || 0);
    setVal('count-reserved', counts.RESERVED || 0); 
    setVal('count-maintenance', counts.MAINTENANCE || 0);
}

function filterPC(status) {
    currentFilter = status.toUpperCase();
    if (status === 'all') currentFilter = 'all';
    
    document.querySelectorAll('#realtime-filters button').forEach(btn => {
        btn.classList.remove('active');
        btn.style.backgroundColor = 'transparent';
        btn.style.color = '#6c757d'; 
    });

    const activeBtn = document.getElementById(`btn-${status}`);
    if (activeBtn) {
        activeBtn.classList.add('active');
        if(status === 'all') { activeBtn.style.backgroundColor = '#e9ecef'; activeBtn.style.color = '#495057'; activeBtn.style.border = 'none'; }
        else if(status === 'available') { activeBtn.style.backgroundColor = '#198754'; activeBtn.style.color = 'white'; }
        else if(status === 'in_use') { activeBtn.style.backgroundColor = '#dc3545'; activeBtn.style.color = 'white'; }
        else if(status === 'reserved') { activeBtn.style.backgroundColor = '#ffc107'; activeBtn.style.color = 'black'; }
        else if(status === 'maintenance') { activeBtn.style.backgroundColor = '#6c757d'; activeBtn.style.color = 'white'; }
    }
    
    renderMonitor();
}

// ==========================================
// 🛠️ Admin Actions (Check-in / Check-out)
// ==========================================

function openManageActiveModal(pcId, userName) {
    document.getElementById('managePcId').value = pcId;
    document.getElementById('managePcName').innerText = `Station: ${pcId}`;
    document.getElementById('manageUserName').innerText = userName || 'ไม่ทราบชื่อ';
    if(manageActiveModal) manageActiveModal.show();
}

async function confirmForceLogout() {
    const pcId = document.getElementById('managePcId').value;
    if (!pcId) return;

    if(!confirm(`ยืนยันสั่งบังคับเช็คเอาท์ (Force Check-out) เครื่อง ${pcId} ใช่หรือไม่?`)) return;

    try {
        const response = await fetch(`/kiosk/admin-portal/checkout/${pcId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCsrfToken(), 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            if(manageActiveModal) manageActiveModal.hide();
            renderMonitor(); 
        } else {
            alert(`เกิดข้อผิดพลาด: ${data.message}`);
        }
    } catch (error) {
        alert("ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้");
    }
}

function openCheckInModal(pcId) {
    document.getElementById('checkInPcId').value = pcId;
    document.getElementById('modalPcName').innerText = `Station: ${pcId}`;
    switchTab('internal'); 
    document.getElementById('ubuUser').value = '';
    document.getElementById('extIdCard').value = '';
    document.getElementById('extName').value = '';
    document.getElementById('extOrg').value = '';
    document.getElementById('internalVerifyCard').classList.add('d-none');
    verifiedUserData = null;
    checkConfirmButtonState();
    if(checkInModal) checkInModal.show();
}

function switchTab(tabName) {
    currentTab = tabName;
    const btnInt = document.getElementById('tab-internal'); const btnExt = document.getElementById('tab-external');
    const formInt = document.getElementById('formInternal'); const formExt = document.getElementById('formExternal');
    
    if (tabName === 'internal') {
        btnInt.classList.add('active'); btnExt.classList.remove('active');
        formInt.classList.remove('d-none'); formExt.classList.add('d-none');
    } else {
        btnExt.classList.add('active'); btnInt.classList.remove('active');
        formExt.classList.remove('d-none'); formInt.classList.add('d-none');
    }
    checkConfirmButtonState();
}

function checkConfirmButtonState() {
    const btnConfirm = document.getElementById('btnConfirm');
    btnConfirm.disabled = (currentTab === 'internal') ? !verifiedUserData : false;
}

async function verifyUBUUser() {
    const userIdInput = document.getElementById('ubuUser');
    const userId = userIdInput.value.trim();
    const verifyBtn = document.querySelector('button[onclick="verifyUBUUser()"]');
    
    if (!userId) { alert('กรุณากรอกรหัสนักศึกษา / บุคลากร'); return; }
    
    const originalBtnText = verifyBtn.innerHTML;
    verifyBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
    verifyBtn.disabled = true;
    
    try {
        const response = await fetch('/kiosk/api/verify-user/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify({ student_id: userId }) 
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            verifiedUserData = { 
                id: data.data.id, name: data.data.name, faculty: data.data.faculty,
                role: data.data.role || 'student', year: data.data.year || '-'
            };
            document.getElementById('internalVerifyCard').classList.remove('d-none');
            document.getElementById('showName').innerText = verifiedUserData.name;
            document.getElementById('showFaculty').innerText = verifiedUserData.faculty;
            checkConfirmButtonState();
        } else {
            alert(`❌ ${data.message}`);
            document.getElementById('internalVerifyCard').classList.add('d-none');
            verifiedUserData = null;
            checkConfirmButtonState();
        }
    } catch (error) {
        alert('เชื่อมต่อ API ล้มเหลว กรุณาลองใหม่');
    } finally {
        verifyBtn.innerHTML = originalBtnText;
        verifyBtn.disabled = false;
    }
}

async function submitAdminCheckIn() {
    const pcId = document.getElementById('checkInPcId').value;
    let payload = {};

    if (currentTab === 'internal') {
        if (!verifiedUserData) return;
        payload = {
            user_id: verifiedUserData.id, user_name: verifiedUserData.name,
            department: verifiedUserData.faculty, user_type: verifiedUserData.role, 
            user_year: verifiedUserData.year
        };
    } else {
        payload = {
            user_id: document.getElementById('extIdCard').value.trim(),
            user_name: document.getElementById('extName').value.trim(),
            department: document.getElementById('extOrg').value.trim() || 'บุคคลทั่วไป',
            user_type: 'guest', user_year: '-'
        };
        if (!payload.user_id || !payload.user_name) { alert('กรุณากรอกข้อมูลให้ครบถ้วน'); return; }
    }

    const confirmBtn = document.getElementById('btnConfirm');
    confirmBtn.disabled = true;

    try {
        const response = await fetch(`/kiosk/admin-portal/checkin/${pcId}/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if(data.status === 'success') {
            if(checkInModal) checkInModal.hide();
            renderMonitor();
        } else { alert(data.message); }
    } catch (error) { alert("บันทึกข้อมูลไม่สำเร็จ"); }
    finally { confirmBtn.disabled = false; }
}