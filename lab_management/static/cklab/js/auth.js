/* auth.js - Kiosk Logic (Django Integrated Version with UBU API) */

function getSystemPCId() {
    // ดึงค่า pc จาก Hash (เช่น #PC-01) หรือ Query Parameter (เช่น ?pc=PC-01)
    if (window.location.hash) {
        return window.location.hash.replace('#', '').trim();
    }
    const params = new URLSearchParams(window.location.search);
    return params.get('pc');
}

// ฟังก์ชันสำหรับดึง CSRF Token ของ Django จาก Cookie
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

document.addEventListener('DOMContentLoaded', () => {
    // Setup Modal
    const modalEl = document.getElementById('labClosedModal');
    if (modalEl) labClosedModal = new bootstrap.Modal(modalEl);

    // Validate PC ID (แก้ไข: เช็คแค่ว่ามีค่าส่งมาหรือไม่ ไม่ต้องเช็คว่าเป็นตัวเลข)
    if (!FIXED_PC_ID) {
        renderNoPcIdError();
        return;
    }

    // Monitor Status ผ่าน Django API
    fetchMachineAndLabStatus();
    setInterval(fetchMachineAndLabStatus, 3000); // ดึงข้อมูลทุก 3 วินาที

    // Bind Events
    const extInputs = document.querySelectorAll('#formExternal input');
    if(extInputs.length > 0) extInputs.forEach(input => input.addEventListener('input', validateForm));
    
    // Smart Enter Logic
    const ubuInput = document.getElementById('ubuUser');
    if(ubuInput) {
        ubuInput.addEventListener('keydown', (e) => { 
            if (e.key === 'Enter') {
                if (!verifiedUserData) {
                    verifyUBUUser(); // ยังไม่ผ่าน -> ตรวจสอบ
                } else {
                    confirmCheckIn(); // ผ่านแล้ว -> เข้าใช้งานเลย
                }
            } 
        });
    }
});

// ✅ ดึงสถานะเครื่องและสถานะแล็บจาก Backend
async function fetchMachineAndLabStatus() {
    try {
        // ใช้ relative path เพื่อให้รองรับทั้ง / และ /kiosk/
        const response = await fetch(`/api/status/${FIXED_PC_ID}/`);
        if (!response.ok) return;

        const data = await response.json();
        
        // 1. จัดการสถานะปิด/เปิด แล็บ (Lab Status)
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

        // 2. จัดการสถานะเครื่อง (Machine Status)
        const indicator = document.querySelector('.status-indicator');
        if(indicator) {
            indicator.className = 'status-indicator rounded-circle d-inline-block';
            indicator.style.width = '10px';
            indicator.style.height = '10px';
            indicator.style.marginRight = '6px';
            
            if(data.status === 'AVAILABLE') indicator.classList.add('bg-success');
            else if(data.status === 'IN_USE') indicator.classList.add('bg-danger');
            else if(data.status === 'RESERVED') indicator.classList.add('bg-warning');
            else indicator.classList.add('bg-secondary'); // MAINTENANCE
        }

        // เก็บสถานะลง attribute ของปุ่มเพื่อให้ validateForm เอาไปเช็คต่อ
        const btnConfirm = document.getElementById('btnConfirm');
        if(btnConfirm) {
            btnConfirm.dataset.pcStatus = data.status;
            validateForm(); // รีเฟรชปุ่มเมื่อสถานะเครื่องเปลี่ยน
        }

    } catch (error) {
        console.error("Error fetching status:", error);
    }
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
    
    // Reset Internal Form
    document.getElementById('ubuUser').value = '';
    document.getElementById('internalVerifyCard').classList.add('d-none');
    const errEl = document.getElementById('loginError');
    if(errEl) errEl.classList.add('d-none');

    if(type === 'internal') {
        if(btnInt) btnInt.classList.add('active'); 
        if(btnExt) btnExt.classList.remove('active');
        document.getElementById('formInternal').classList.remove('d-none');
        document.getElementById('formExternal').classList.add('d-none');
    } else {
        if(btnExt) btnExt.classList.add('active'); 
        if(btnInt) btnInt.classList.remove('active');
        document.getElementById('formExternal').classList.remove('d-none');
        document.getElementById('formInternal').classList.add('d-none');
    }
    validateForm();
}

// ✅ ฟังก์ชันตรวจสอบผู้ใช้ (ยิง API ไปหา Django Backend ซึ่งจะไปคุยกับ UBU API ต่อ)
async function verifyUBUUser() {
    const input = document.getElementById('ubuUser');
    const id = input.value.trim();
    if(!id) { input.focus(); return; }
    
    const verifyCard = document.getElementById('internalVerifyCard');
    const errEl = document.getElementById('loginError');
    
    // ปิดปุ่มตรวจสอบชั่วคราวขณะโหลด และเปลี่ยนข้อความ
    const checkBtn = input.nextElementSibling;
    const originalBtnText = checkBtn.innerHTML;
    checkBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    checkBtn.disabled = true;

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
            // ดึงข้อมูลที่ได้จาก UBU API ผ่าน Django มาแสดงผล
            verifiedUserData = result.data;
            
            document.getElementById('showName').innerText = verifiedUserData.name;
            document.getElementById('showFaculty').innerText = verifiedUserData.faculty;
            const roleEl = document.getElementById('showRole');
            if(roleEl) roleEl.innerText = verifiedUserData.role.toUpperCase();
            
            verifyCard.classList.remove('d-none');
            if(errEl) errEl.classList.add('d-none'); // ซ่อน Error

            validateForm();
        } else {
            // ไม่พบข้อมูล หรือ Error
            throw new Error(result.message || "ไม่พบข้อมูลในระบบ");
        }

    } catch (error) {
        console.error("Verification Error:", error);
        
        if(errEl) {
            errEl.innerHTML = `<i class="bi bi-exclamation-circle-fill me-1"></i> ${error.message}`;
            errEl.classList.remove('d-none');
            input.classList.add('is-invalid');
            setTimeout(() => input.classList.remove('is-invalid'), 2000);
        } else {
            alert(`❌ ${error.message}`);
        }
        
        verifyCard.classList.add('d-none');
        verifiedUserData = null;
        input.value = ''; input.focus(); validateForm();
    } finally {
        // คืนค่าปุ่มกลับเหมือนเดิม
        checkBtn.innerHTML = originalBtnText;
        checkBtn.disabled = false;
    }
}

function validateForm() {
    let isUserValid = false;
    const btn = document.getElementById('btnConfirm');
    if (!btn) return;

    if (activeTab === 'internal') isUserValid = (verifiedUserData !== null);
    else {
        const id = document.getElementById('extIdCard').value.trim();
        const name = document.getElementById('extName').value.trim();
        isUserValid = (id !== '' && name !== '');
    }
    
    // เช็คสถานะเครื่องจาก data-attribute ที่ถูกดึงมาจาก Backend
    const pcStatus = btn.dataset.pcStatus || 'UNKNOWN';
    const isAccessible = (pcStatus === 'AVAILABLE' || pcStatus === 'RESERVED');
    
    if (isUserValid && isAccessible) {
        btn.disabled = false;
        btn.className = 'btn btn-success w-100 py-3 fw-bold shadow-sm rounded-3 transition-btn';
        if (pcStatus === 'RESERVED') btn.innerHTML = `<i class="bi bi-calendar-check me-2"></i>ยืนยันการเข้าใช้งาน (ตามที่จองไว้)`;
        else btn.innerHTML = `<i class="bi bi-box-arrow-in-right me-2"></i>เข้าสู่ระบบและเริ่มใช้งาน`;
    } else {
        btn.disabled = true;
        btn.className = 'btn btn-secondary w-100 py-3 fw-bold shadow-sm rounded-3 transition-btn';
        if (!isAccessible) btn.innerHTML = `<i class="bi bi-x-circle me-2"></i>เครื่องไม่ว่าง (${pcStatus})`;
        else btn.innerHTML = `<i class="bi bi-box-arrow-in-right me-2"></i>เข้าสู่ระบบและเริ่มใช้งาน`;
    }
}

// ✅✅✅ MAIN CONFIRM FUNCTION (ส่งข้อมูลไปให้ Django CheckinView) ✅✅✅
function confirmCheckIn() {
    if (!verifiedUserData && activeTab === 'internal') return;
    
    if (activeTab === 'external') {
        verifiedUserData = {
            id: document.getElementById('extIdCard').value.trim(),
            name: document.getElementById('extName').value.trim(),
            faculty: document.getElementById('extOrg').value.trim() || 'บุคคลทั่วไป',
            role: 'guest', // ตรงกับ choices ใน model
            level: 'บุคคลทั่วไป',
            year: '-'
        };
    }

    // เซฟชื่อลง SessionStorage เผื่อเอาไปแสดงหน้า Timer
    sessionStorage.setItem('cklab_user_name', verifiedUserData.name);

    // สร้าง Form แบบไดนามิก เพื่อ POST ข้อมูลไปยัง CheckinView ของ Django
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/checkin/${FIXED_PC_ID}/`; // URL ตามโครงสร้าง Django

    // เพิ่ม CSRF Token
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = getCookie('csrftoken');
    form.appendChild(csrfInput);

    // เพิ่มข้อมูลผู้ใช้
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

    // นำ Form ใส่ใน Body แล้ว Submit
    document.body.appendChild(form);
    form.submit();
}