/* auth.js - Kiosk Logic (Django Integrated Version with UBU API) */

function getSystemPCId() {
    if (window.location.hash) {
        return window.location.hash.replace('#', '').trim();
    }
    const params = new URLSearchParams(window.location.search);
    return params.get('pc');
}

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

const FIXED_PC_ID = getSystemPCId(); 

let verifiedUserData = null;
let activeTab = 'internal';
let lastLabStatus = null;
let labClosedModal = null;
let isVerifying = false; // ✅ ตัวแปรป้องกันการกดปุ่มตรวจสอบรัวๆ (Double Submit)
let reservedStudentId = null; // รหัสนักศึกษาที่จองเครื่องนี้ไว้ (null = ไม่มีการจอง)

document.addEventListener('DOMContentLoaded', () => {
    const modalEl = document.getElementById('labClosedModal');
    if (modalEl) labClosedModal = new bootstrap.Modal(modalEl);

    if (!FIXED_PC_ID) {
        renderNoPcIdError();
        return;
    }

    fetchMachineAndLabStatus();
    setInterval(fetchMachineAndLabStatus, 3000); 

    const extInputs = document.querySelectorAll('#formExternal input');
    if(extInputs.length > 0) extInputs.forEach(input => input.addEventListener('input', validateForm));
    
    const ubuInput = document.getElementById('ubuUser');
    if(ubuInput) {
        ubuInput.addEventListener('keydown', (e) => { 
            if (e.key === 'Enter') {
                e.preventDefault(); 
                if (!verifiedUserData) {
                    verifyUBUUser(); 
                } else {
                    const btn = document.getElementById('btnConfirm');
                    if(btn && !btn.disabled) confirmCheckIn(); 
                }
            } 
        });
        
        // ✅ อัปเดต: ทันทีที่เริ่มพิมพ์ใหม่ ให้ซ่อนกล่อง Error และเอาขอบแดงออกทันที
        ubuInput.addEventListener('input', () => {
            const errEl = document.getElementById('loginError');
            if(errEl) errEl.classList.add('d-none');
            ubuInput.classList.remove('is-invalid');

            if(verifiedUserData) {
                verifiedUserData = null;
                const verifyCard = document.getElementById('internalVerifyCard');
                if(verifyCard) verifyCard.classList.add('d-none');
                validateForm();
            }
        });
    }
});

async function fetchMachineAndLabStatus() {
    try {
        let fetchUrl = `/api/status/${FIXED_PC_ID}/`;
        if (window.location.pathname.includes('/kiosk/')) {
            fetchUrl = `/kiosk/api/status/${FIXED_PC_ID}/`;
        }

        const response = await fetch(fetchUrl);
        if (!response.ok) {
            const btnConfirm = document.getElementById('btnConfirm');
            if (btnConfirm && !btnConfirm.dataset.pcStatus) {
                btnConfirm.dataset.pcStatus = 'AVAILABLE';
                validateForm();
            }
            return;
        }

        const data = await response.json();
        
        const currentStatus = data.is_open ? 'open' : 'closed';
        if (currentStatus === 'closed') {
            if (labClosedModal) {
                const el = document.getElementById('labClosedModal');
                if (!el.classList.contains('show')) labClosedModal.show();
            }
        } else if (currentStatus === 'open') {
            if (lastLabStatus === 'closed') {
                if (labClosedModal) labClosedModal.hide();
                window.location.reload(); 
            }
        }
        lastLabStatus = currentStatus;

        const indicator = document.querySelector('.status-indicator');
        if(indicator) {
            indicator.className = 'status-indicator rounded-circle d-inline-block';
            indicator.style.width = '10px';
            indicator.style.height = '10px';
            indicator.style.marginRight = '6px';
            
            if(data.status === 'AVAILABLE') indicator.classList.add('bg-success');
            else if(data.status === 'IN_USE') indicator.classList.add('bg-danger');
            else if(data.status === 'RESERVED') indicator.classList.add('bg-warning');
            else indicator.classList.add('bg-secondary'); 
        }

        // เก็บรหัสนักศึกษาที่จองเครื่องนี้ไว้ เพื่อใช้ตรวจสอบตอน validateForm
        reservedStudentId = data.next_booking_student_id || null;
        renderReservedNotice(data.status, reservedStudentId);

        const btnConfirm = document.getElementById('btnConfirm');
        if(btnConfirm) {
            btnConfirm.dataset.pcStatus = data.status;
            validateForm();
        }

    } catch (error) {
        console.error("Error fetching status:", error);
    }
}

function renderReservedNotice(status, studentId) {
    let notice = document.getElementById('reservedNotice');
    if (status !== 'RESERVED') {
        if (notice) notice.remove();
        return;
    }
    if (!notice) {
        notice = document.createElement('div');
        notice.id = 'reservedNotice';
        notice.className = 'alert alert-warning border-warning fw-bold small rounded-3 mb-3 py-2 px-3';
        // แทรกก่อนปุ่ม Confirm
        const btn = document.getElementById('btnConfirm');
        if (btn) btn.parentNode.insertBefore(notice, btn);
    }
    notice.innerHTML = `<i class="bi bi-lock-fill me-2"></i>เครื่องนี้ถูกจองไว้แล้ว — กรุณากรอกรหัสเฉพาะผู้จองเท่านั้น`;
}

function renderNoPcIdError() {
    document.body.innerHTML = `
        <div class="d-flex justify-content-center align-items-center vh-100 flex-column text-center bg-light">
            <div class="card border-0 shadow p-5 rounded-4">
                <h2 class="fw-bold text-dark">⚠️ Setup Error</h2>
                <p class="text-muted mb-4">ไม่พบหมายเลขเครื่องใน URL<br>กรุณาเข้าผ่านลิงก์เช่น: <code>/?pc=PC-01</code></p>
            </div>
        </div>
    `;
}

function switchTab(type) {
    activeTab = type;
    verifiedUserData = null;
    const btnInt = document.getElementById('tab-internal');
    const btnExt = document.getElementById('tab-external');
    
    const ubuUserEl = document.getElementById('ubuUser');
    if(ubuUserEl) {
        ubuUserEl.value = '';
        ubuUserEl.classList.remove('is-invalid');
    }
    
    const verifyCard = document.getElementById('internalVerifyCard');
    if(verifyCard) verifyCard.classList.add('d-none');
    
    const errEl = document.getElementById('loginError');
    if(errEl) errEl.classList.add('d-none');

    const formInt = document.getElementById('formInternal');
    const formExt = document.getElementById('formExternal');

    if(type === 'internal') {
        if(btnInt) btnInt.classList.add('active'); 
        if(btnExt) btnExt.classList.remove('active');
        if(formInt) formInt.classList.remove('d-none');
        if(formExt) formExt.classList.add('d-none');
    } else {
        if(btnExt) btnExt.classList.add('active'); 
        if(btnInt) btnInt.classList.remove('active');
        if(formExt) formExt.classList.remove('d-none');
        if(formInt) formInt.classList.add('d-none');
    }
    validateForm();
}

async function verifyUBUUser() {
    // ✅ อัปเดต: ถ้ากำลังโหลดอยู่ ห้ามทำซ้ำ
    if (isVerifying) return; 

    const input = document.getElementById('ubuUser');
    if(!input) return;
    
    const id = input.value.trim();
    if(!id) { input.focus(); return; }
    
    isVerifying = true; // ล็อกปุ่ม
    
    const verifyCard = document.getElementById('internalVerifyCard');
    const errEl = document.getElementById('loginError');
    
    // ซ่อน Error ก่อนเริ่มเช็คอันใหม่
    if(errEl) errEl.classList.add('d-none');
    input.classList.remove('is-invalid');

    const checkBtn = input.nextElementSibling;
    if (checkBtn) {
        checkBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        checkBtn.disabled = true;
    }

    try {
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
            verifiedUserData = result.data;
            
            const nameToCheck = verifiedUserData.name || "";
            const idToCheck = String(verifiedUserData.id || "");
            
            const isStaffByName = nameToCheck.includes("อาจารย์") || nameToCheck.includes("ดร.") || nameToCheck.includes("ผศ.") || nameToCheck.includes("รศ.");
            const isStaffById = !/^\d+$/.test(idToCheck); 

            if (isStaffByName || isStaffById) {
                verifiedUserData.role = 'staff'; 
                verifiedUserData.year = '-';
            }

            const showNameEl = document.getElementById('showName');
            const showFacultyEl = document.getElementById('showFaculty');
            const showRoleEl = document.getElementById('showRole');
            
            if(showNameEl) showNameEl.innerText = verifiedUserData.name;
            if(showFacultyEl) showFacultyEl.innerText = verifiedUserData.faculty;
            
            if(showRoleEl) {
                if (verifiedUserData.role === 'staff') {
                    showRoleEl.innerText = 'STAFF (บุคลากร)';
                    showRoleEl.className = 'badge bg-success bg-opacity-10 text-success border border-success px-3 py-2 rounded-pill mt-1';
                } else {
                    showRoleEl.innerText = 'STUDENT (นักศึกษา)';
                    showRoleEl.className = 'badge bg-primary bg-opacity-10 text-primary border border-primary px-3 py-2 rounded-pill mt-1';
                }
            }
            
            if(verifyCard) verifyCard.classList.remove('d-none');
            validateForm();
        } else {
            throw new Error(result.message || "ไม่พบข้อมูลในระบบ");
        }

    } catch (error) {
        console.error("Verification Error:", error);
        
        if(errEl) {
            errEl.innerHTML = `<i class="bi bi-exclamation-circle-fill me-1"></i> ${error.message}`;
            errEl.classList.remove('d-none');
            input.classList.add('is-invalid');
        } else {
            alert(`❌ ${error.message}`);
        }
        
        if(verifyCard) verifyCard.classList.add('d-none');
        verifiedUserData = null;
        input.focus(); 
        validateForm();
    } finally {
        isVerifying = false; // ปลดล็อก
        if (checkBtn) {
            checkBtn.innerHTML = "ตรวจสอบ"; 
            checkBtn.disabled = false;
        }
    }
}

function validateForm() {
    let isUserValid = false;
    const btn = document.getElementById('btnConfirm');
    if (!btn) return;

    if (activeTab === 'internal') {
        isUserValid = (verifiedUserData !== null);
    } else {
        const idEl = document.getElementById('extIdCard');
        const nameEl = document.getElementById('extName');
        const id = idEl ? idEl.value.trim() : '';
        const name = nameEl ? nameEl.value.trim() : '';
        isUserValid = (id !== '' && name !== '');
    }
    
    // ✅ อัปเดต: เปลี่ยนค่าเริ่มต้นจาก 'UNKNOWN' เป็น 'AVAILABLE'
    // หากดึงข้อมูลสถานะไม่ทันหรือไม่สำเร็จ ปุ่มจะได้ไม่โดนล็อก
    const pcStatus = btn.dataset.pcStatus || 'AVAILABLE';
    const isAccessible = (pcStatus === 'AVAILABLE' || pcStatus === 'RESERVED');

    // ถ้าเครื่อง RESERVED ต้องตรวจสอบว่ารหัสที่กรอกตรงกับผู้จองไว้
    let isReservedAllowed = true;
    if (pcStatus === 'RESERVED' && reservedStudentId) {
        const enteredId = verifiedUserData ? String(verifiedUserData.id).trim() : '';
        isReservedAllowed = (enteredId === String(reservedStudentId).trim());
    }

    if (isUserValid && isAccessible && isReservedAllowed) {
        btn.disabled = false;
        btn.className = 'btn btn-success w-100 py-3 fw-bold shadow-sm rounded-3 transition-btn';
        if (pcStatus === 'RESERVED') {
            btn.innerHTML = `<i class="bi bi-calendar-check me-2"></i>ยืนยันการเข้าใช้งาน (ตามที่จองไว้)`;
        } else {
            btn.innerHTML = `<i class="bi bi-box-arrow-in-right me-2"></i>เข้าสู่ระบบและเริ่มใช้งาน`;
        }
    } else {
        btn.disabled = true;
        btn.className = 'btn btn-secondary w-100 py-3 fw-bold shadow-sm rounded-3 transition-btn';
        if (!isAccessible) {
            btn.innerHTML = `<i class="bi bi-x-circle me-2"></i>เครื่องไม่ว่าง (${pcStatus})`;
        } else if (pcStatus === 'RESERVED' && isUserValid && !isReservedAllowed) {
            btn.innerHTML = `<i class="bi bi-shield-lock me-2"></i>รหัสไม่ตรงกับผู้จอง`;
        } else {
            btn.innerHTML = `<i class="bi bi-box-arrow-in-right me-2"></i>เข้าสู่ระบบและเริ่มใช้งาน`;
        }
    }
}

// ✅✅✅ MAIN CONFIRM FUNCTION (ส่งข้อมูลไปให้ Django CheckinView) ✅✅✅
function confirmCheckIn() {
    if (!verifiedUserData && activeTab === 'internal') return;
    
    if (activeTab === 'external') {
        const idEl = document.getElementById('extIdCard');
        const nameEl = document.getElementById('extName');
        const orgEl = document.getElementById('extOrg');
        
        verifiedUserData = {
            id: idEl ? idEl.value.trim() : '',
            name: nameEl ? nameEl.value.trim() : '',
            faculty: (orgEl && orgEl.value.trim() !== '') ? orgEl.value.trim() : 'บุคคลทั่วไป',
            role: 'guest', 
            level: 'บุคคลทั่วไป',
            year: '-'
        };
    }

    sessionStorage.setItem('cklab_user_name', verifiedUserData.name);

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/checkin/${FIXED_PC_ID}/`; 

    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = getCookie('csrftoken');
    form.appendChild(csrfInput);

    const dataToSubmit = {
        'user_id': verifiedUserData.id,
        'user_name': verifiedUserData.name,
        'user_type': verifiedUserData.role,
        'department': verifiedUserData.faculty,
        'user_year': verifiedUserData.year
    };

    for (const [key, value] of Object.entries(dataToSubmit)) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = value;
        form.appendChild(input);
    }

    document.body.appendChild(form);
    form.submit();
}