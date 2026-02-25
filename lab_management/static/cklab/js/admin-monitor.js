/* admin-monitor.js (Django API Version) */

let checkInModal, manageActiveModal;
let currentTab = 'internal';
let verifiedUserData = null;
let currentFilter = 'all'; 

// ฟังก์ชันสำหรับดึง CSRF Token จาก HTML
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

document.addEventListener('DOMContentLoaded', () => {
    // 1. Init Modals
    const modalEl = document.getElementById('checkInModal');
    if (modalEl) checkInModal = new bootstrap.Modal(modalEl);
    
    const manageEl = document.getElementById('manageActiveModal');
    if (manageEl) manageActiveModal = new bootstrap.Modal(manageEl);

    // 2. จัดการ Event การสลับ Tab เพื่อซ่อน/โชว์ ปุ่ม Filter
    const tabRealtime = document.getElementById('tab-realtime');
    const tabBooking = document.getElementById('tab-booking');
    const realtimeFilters = document.getElementById('realtime-filters');

    if (tabRealtime && tabBooking && realtimeFilters) {
        tabRealtime.addEventListener('shown.bs.tab', function () {
            realtimeFilters.classList.remove('d-none');
            realtimeFilters.classList.add('d-flex');
        });
        
        tabBooking.addEventListener('shown.bs.tab', function () {
            realtimeFilters.classList.remove('d-flex');
            realtimeFilters.classList.add('d-none');
        });
    }

    // 3. Start Logic
    renderMonitor();
    updateClock();

    // 4. Auto Refresh (ทุก 5 วินาที)
    setInterval(() => {
        const isModalOpen = (modalEl && modalEl.classList.contains('show')) || (manageEl && manageEl.classList.contains('show'));
        if (!isModalOpen) renderMonitor();
    }, 5000); 
    
    setInterval(updateClock, 1000);
});

function updateClock() {
    const now = new Date();
    const clockEl = document.getElementById('clockDisplay');
    if(clockEl) clockEl.innerText = now.toLocaleTimeString('th-TH');
}

// ==========================================
// 🖥️ Render Monitor Grid (UI) 
// ==========================================

function filterPC(status) {
    currentFilter = status.toUpperCase();
    if (status === 'all') currentFilter = 'all';
    updateFilterButtons(status.toLowerCase());
    renderMonitor();
}

function updateMonitorStats(counts) {
    const setVal = (id, val) => {
        const el = document.getElementById(id);
        if(el) {
            el.innerText = val || 0;
            el.style.transition = 'transform 0.2s';
            el.style.transform = 'scale(1.2)';
            setTimeout(() => el.style.transform = 'scale(1)', 200);
        }
    };
    setVal('count-available', counts.available);
    setVal('count-in_use', counts.in_use);
    setVal('count-reserved', counts.reserved || 0); 
    setVal('count-maintenance', counts.maintenance || 0);
}

async function renderMonitor() {
    const grid = document.getElementById('monitorGrid');
    if(!grid) return;

    try {
        const response = await fetch('/admin-portal/monitor/', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        
        const data = await response.json();
        if (data.status !== 'success') return;

        const allPcs = data.pcs;
        updateMonitorStats(data.counts);

        let displayPcs = allPcs;
        if (currentFilter !== 'all') {
            displayPcs = displayPcs.filter(pc => pc.status === currentFilter);
        }

        grid.innerHTML = '';
        if (displayPcs.length === 0) {
            grid.innerHTML = `<div class="col-12 text-center text-muted py-5 fw-bold"><i class="bi bi-inbox fs-1 d-block mb-2 text-secondary"></i>ไม่พบข้อมูลเครื่องคอมพิวเตอร์</div>`;
            return;
        }

        displayPcs.forEach(pc => {
            let statusClass = '', iconClass = '', label = '', cardBorder = '';
            
            switch(pc.status) {
                case 'AVAILABLE': statusClass = 'text-success'; cardBorder = 'border-success'; iconClass = 'bi-check-circle'; label = 'ว่าง'; break;
                case 'IN_USE': statusClass = 'text-danger'; cardBorder = 'border-danger'; iconClass = 'bi-person-workspace'; label = 'ใช้งานอยู่'; break;
                case 'RESERVED': statusClass = 'text-warning'; cardBorder = 'border-warning'; iconClass = 'bi-bookmark-fill'; label = 'จองแล้ว'; break;
                default: statusClass = 'text-secondary'; cardBorder = 'border-secondary'; iconClass = 'bi-wrench-adjustable'; label = 'แจ้งซ่อม';
            }

            const userDisplay = pc.user_name ? 
                `<div class="mt-1 fw-bold text-dark text-truncate" title="${pc.user_name}"><i class="bi bi-person-fill"></i> ${pc.user_name}</div>` : 
                `<div class="mt-1 text-muted">-</div>`;

            let softwareHtml = '';
            if (pc.software && pc.software !== '-') {
                softwareHtml = `<div class="mt-2 d-flex flex-wrap justify-content-center gap-1"><span class="badge bg-light text-secondary border" style="font-size: 0.65rem;">${pc.software}</span></div>`;
            } else {
                softwareHtml = '<div class="mt-2" style="height: 22px;"></div>';
            }

            const codeNameHtml = pc.codeName ? ` <small class="text-muted fw-normal" style="font-size: 0.8rem;">| ${pc.codeName}</small>` : '';

            grid.innerHTML += `
                <div class="col-6 col-md-4 col-lg-3">
                    <div class="card h-100 shadow-sm ${cardBorder} position-relative pc-card-hover" 
                         onclick="handlePcClick('${pc.id}', '${pc.status}', '${pc.user_name || ''}')"
                         data-software="${pc.software}">
                        <div class="card-body text-center p-3 d-flex flex-column">
                            <i class="bi ${iconClass} display-6 ${statusClass} mb-2"></i>
                            <h5 class="fw-bold mb-0 text-dark">${pc.name}${codeNameHtml}</h5>
                            <div class="badge bg-light text-dark border mb-1 align-self-center mt-1">${label}</div>
                            
                            ${userDisplay}
                            ${softwareHtml}
                            
                            <div class="mt-auto w-100 pt-3 border-top mt-3">
                                <small class="text-muted" style="font-size: 0.7rem;">อัปเดตล่าสุด: ${pc.last_updated}</small>
                            </div>
                        </div>
                    </div>
                </div>`;
        });
    } catch (error) {
        console.error("Error fetching monitor data:", error);
    }
}

function handlePcClick(pcId, status, userName) {
    if (status === 'AVAILABLE') {
        openCheckInModal(pcId);
    } else if (status === 'IN_USE') {
        openManageActiveModal(pcId, userName);
    } else if (status === 'RESERVED') {
        alert("ระบบจัดการการจองจาก Admin กำลังอยู่ในช่วงพัฒนาครับ");
    } else {
        alert(`เครื่องนี้สถานะ แจ้งซ่อม ไม่สามารถใช้งานได้`);
    }
}

// ==========================================
// 🛠️ Admin Force Check-out
// ==========================================

function openManageActiveModal(pcId, userName) {
    document.getElementById('managePcId').value = pcId;
    document.getElementById('managePcName').innerText = `Station: ${pcId}`;
    document.getElementById('manageUserName').innerText = userName || 'Unknown';
    if(manageActiveModal) manageActiveModal.show();
}

async function confirmForceLogout() {
    const pcId = document.getElementById('managePcId').value;
    if (!pcId) return;

    if(confirm(`ยืนยันสั่งบังคับเช็คเอาท์ (Force Check-out) เครื่อง ${pcId} ใช่หรือไม่?`)) {
        try {
            const response = await fetch(`/admin-portal/checkout/${pcId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                if(manageActiveModal) manageActiveModal.hide();
                renderMonitor(); 
            } else {
                alert(`เกิดข้อผิดพลาด: ${data.message}`);
            }
        } catch (error) {
            console.error(error);
            alert("ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้");
        }
    }
}

// ==========================================
// 📝 Admin Force Check-in Logic
// ==========================================

function openCheckInModal(pcId) {
    document.getElementById('checkInPcId').value = pcId;
    document.getElementById('modalPcName').innerText = `Station: ${pcId}`;

    switchTab('internal'); 
    ['ubuUser', 'extIdCard', 'extName', 'extOrg'].forEach(id => {
        if(document.getElementById(id)) document.getElementById(id).value = '';
    });
    document.getElementById('internalVerifyCard').classList.add('d-none');
    document.getElementById('btnConfirm').disabled = true;
    verifiedUserData = null;

    if(checkInModal) checkInModal.show();
}

async function verifyUBUUser() {
    const userIdInput = document.getElementById('ubuUser');
    const userId = userIdInput.value.trim();
    
    // หา Element ปุ่มตรวจสอบเพื่อทำ Loading Effect
    const verifyBtn = document.querySelector('button[onclick="verifyUBUUser()"]');
    
    if (!userId) { alert('กรุณากรอกรหัสนักศึกษา / บุคลากร'); return; }
    
    // แสดงสถานะ Loading
    const originalBtnText = verifyBtn.innerHTML;
    verifyBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
    verifyBtn.disabled = true;
    
    try {
        const response = await fetch('/api/verify-user/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ student_id: userId }) // ⚠️ จุดที่ 1: คีย์ JSON (student_id)
        });
        
        const data = await response.json();

        if (data.status === 'success') {
            // ดึงข้อมูลออกมารองรับ 2 Format เผื่อ API ส่งมาไม่เหมือนกัน
            const userData = data.data || data; 
            
            verifiedUserData = { 
                id: userId, 
                name: userData.name || userData.first_name || 'ไม่ทราบชื่อ',  // ⚠️ จุดที่ 2: คีย์ชื่อ
                faculty: userData.faculty || userData.department || '-'       // ⚠️ จุดที่ 3: คีย์คณะ
            };
            
            document.getElementById('internalVerifyCard').classList.remove('d-none');
            document.getElementById('showName').innerText = verifiedUserData.name;
            document.getElementById('showFaculty').innerText = verifiedUserData.faculty;
            
            // เปิดให้ปุ่มยืนยันทำงานได้
            const btnConfirm = document.getElementById('btnConfirm');
            btnConfirm.disabled = false;
            btnConfirm.className = 'btn btn-success w-100 py-3 fw-bold shadow-sm rounded-3';
        } else {
            alert(`❌ ${data.message || 'ไม่พบข้อมูลในระบบ'}`);
            document.getElementById('internalVerifyCard').classList.add('d-none');
            verifiedUserData = null;
            document.getElementById('btnConfirm').disabled = true;
        }
    } catch (error) {
        console.error(error);
        alert('เชื่อมต่อ API ล้มเหลว (อาจเป็นเพราะไม่มีอินเทอร์เน็ต หรือ URL ไม่ถูกต้อง)');
    } finally {
        // คืนค่าปุ่มกลับมาเหมือนเดิม
        verifyBtn.innerHTML = originalBtnText;
        verifyBtn.disabled = false;
    }
}

async function confirmCheckIn() {
    const pcId = document.getElementById('checkInPcId').value;
    let finalId = "", finalName = "";

    if (currentTab === 'internal') {
        if (!verifiedUserData) {
            alert('กรุณากดตรวจสอบรหัสก่อนครับ');
            return;
        }
        finalId = verifiedUserData.id;
        finalName = verifiedUserData.name; 
    } else {
        const extIdCard = document.getElementById('extIdCard').value.trim();
        const extName = document.getElementById('extName').value.trim();
        
        if (!extIdCard || !extName) { 
            alert('กรุณากรอก เลขบัตรประชาชน และ ชื่อ-นามสกุล ให้ครบถ้วน'); 
            return; 
        }
        finalId = extIdCard;
        finalName = extName; 
    }

    const confirmBtn = document.getElementById('btnConfirm');
    const originalText = confirmBtn.innerHTML;
    confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> กำลังบันทึก...';
    confirmBtn.disabled = true;

    try {
        const response = await fetch(`/admin-portal/checkin/${pcId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ user_id: finalId, user_name: finalName })
        });

        const data = await response.json();
        
        if(data.status === 'success') {
            if(checkInModal) checkInModal.hide();
            renderMonitor();
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error(error);
        alert("บันทึกข้อมูลไม่สำเร็จ");
    } finally {
        confirmBtn.innerHTML = originalText;
        confirmBtn.disabled = false;
    }
}

// ==========================================
// 🎨 UI Helpers
// ==========================================

function updateFilterButtons(activeStatus) {
    const buttons = ['all', 'available', 'in_use', 'reserved', 'maintenance'];
    buttons.forEach(status => {
        const btn = document.getElementById(`btn-${status}`);
        if(btn) {
            btn.className = "btn btn-sm rounded-pill px-3 me-1";
            btn.style.color = status === activeStatus ? 'white' : '';
            if(status === 'all') { btn.style.backgroundColor = status === activeStatus ? '#495057' : 'transparent'; btn.style.border = '1px solid #ced4da'; }
            if(status === 'available') { btn.style.backgroundColor = status === activeStatus ? '#198754' : 'transparent'; btn.style.border = '1px solid #198754'; }
            if(status === 'in_use') { btn.style.backgroundColor = status === activeStatus ? '#dc3545' : 'transparent'; btn.style.border = '1px solid #dc3545'; }
            if(status === 'reserved') { btn.style.backgroundColor = status === activeStatus ? '#ffc107' : 'transparent'; btn.style.border = '1px solid #ffc107'; if(status===activeStatus) btn.style.color='black'; }
            if(status === 'maintenance') { btn.style.backgroundColor = status === activeStatus ? '#6c757d' : 'transparent'; btn.style.border = '1px solid #6c757d'; }
        }
    });
}

function switchTab(tabName) {
    currentTab = tabName;
    const btnInt = document.getElementById('tab-internal'); const btnExt = document.getElementById('tab-external');
    const formInt = document.getElementById('formInternal'); const formExt = document.getElementById('formExternal');
    const btnConfirm = document.getElementById('btnConfirm');
    if(!btnInt) return;

    if (tabName === 'internal') {
        btnInt.classList.add('btn-primary', 'text-white'); btnInt.classList.remove('btn-light', 'text-muted');
        btnExt.classList.remove('btn-primary', 'text-white'); btnExt.classList.add('btn-light', 'text-muted');
        formInt.classList.remove('d-none'); formExt.classList.add('d-none');
        btnConfirm.disabled = !verifiedUserData;
        btnConfirm.className = verifiedUserData ? 'btn btn-success w-100 py-3 fw-bold shadow-sm rounded-3' : 'btn btn-secondary w-100 py-3 fw-bold shadow-sm rounded-3';
    } else {
        btnExt.classList.add('btn-primary', 'text-white'); btnExt.classList.remove('btn-light', 'text-muted');
        btnInt.classList.remove('btn-primary', 'text-white'); btnInt.classList.add('btn-light', 'text-muted');
        formExt.classList.remove('d-none'); formInt.classList.add('d-none');
        btnConfirm.disabled = false;
        btnConfirm.className = 'btn btn-success w-100 py-3 fw-bold shadow-sm rounded-3';
    }
}