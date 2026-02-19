/* admin-config.js (Cleaned Version: No Zones) */

let adminModal;

document.addEventListener('DOMContentLoaded', () => {
    // 1. เช็ค Database
    if (typeof DB === 'undefined' || typeof DB.getAdmins !== 'function') {
        alert("Critical Error: ไฟล์ mock-db.js ไม่สมบูรณ์");
        return;
    }

    // 2. Init Admin Modal Only
    const adminModalEl = document.getElementById('adminModal');
    if(adminModalEl) adminModal = new bootstrap.Modal(adminModalEl);

    // 3. Render Data
    loadGeneralConfig(); 
    renderAdmins();      

    // 4. Bind Events (เพื่อให้กด Switch ปิดห้องแล้วข้อความเปลี่ยนทันที)
    const switchEl = document.getElementById('labStatusSwitch');
    if (switchEl) {
        switchEl.addEventListener('change', toggleLabStatusUI);
    }
});

// ==========================================
// 1. GENERAL CONFIG FUNCTIONS
// ==========================================

function loadGeneralConfig() {
    const config = DB.getGeneralConfig(); 
    if (!config) return;

    // 1.1 ข้อมูลพื้นฐาน
    if(document.getElementById('confLabName')) document.getElementById('confLabName').value = config.labName || '';
    if(document.getElementById('confLocation')) document.getElementById('confLocation').value = config.labLocation || '';
    if(document.getElementById('confEmail')) document.getElementById('confEmail').value = config.contactEmail || '';
    if(document.getElementById('confMaxTime')) document.getElementById('confMaxTime').value = config.maxDurationMinutes || 180;

    // 1.2 ข้อมูลติดต่อ
    if(document.getElementById('confAdminOnDuty')) {
        document.getElementById('confAdminOnDuty').value = config.adminOnDuty || '';
    }
    if(document.getElementById('confPhone')) {
        document.getElementById('confPhone').value = config.contactPhone || '';
    }

    // 1.3 สถานะห้อง (Lab Status)
    if(document.getElementById('labStatusSwitch')) {
        const isOpen = config.labStatus !== 'closed'; 
        document.getElementById('labStatusSwitch').checked = isOpen;
        toggleLabStatusUI(); 
    }

    // 1.4 ข้อความแจ้งเตือน
    if(document.getElementById('adminMessage')) {
        document.getElementById('adminMessage').value = config.adminMessage || '';
    }
}

function toggleLabStatusUI() {
    const switchEl = document.getElementById('labStatusSwitch');
    const labelEl = document.getElementById('labStatusLabel');
    const msgInput = document.getElementById('adminMessage');
    
    if (switchEl && labelEl) {
        if (switchEl.checked) {
            labelEl.innerText = 'เปิดให้บริการ (Open)';
            labelEl.className = 'form-check-label fw-bold text-success';
            if(msgInput) msgInput.disabled = true; 
        } else {
            labelEl.innerText = 'ปิดปรับปรุงชั่วคราว (Closed)';
            labelEl.className = 'form-check-label fw-bold text-danger';
            if(msgInput) msgInput.disabled = false;
        }
    }
}

function saveGeneralConfig() {
    const currentConfig = DB.getGeneralConfig() || {};
    const isOpen = document.getElementById('labStatusSwitch').checked;
    
    const newConfig = {
        ...currentConfig,
        labName: document.getElementById('confLabName').value.trim(),
        labLocation: document.getElementById('confLocation').value.trim(),
        contactEmail: document.getElementById('confEmail').value.trim(),
        maxDurationMinutes: parseInt(document.getElementById('confMaxTime').value) || 180,
        
        adminOnDuty: document.getElementById('confAdminOnDuty').value.trim(),
        contactPhone: document.getElementById('confPhone').value.trim(),

        labStatus: isOpen ? 'open' : 'closed',
        adminMessage: document.getElementById('adminMessage').value.trim()
    };

    DB.saveGeneralConfig(newConfig);
    alert('✅ บันทึกการตั้งค่าเรียบร้อยแล้ว');
    loadGeneralConfig(); 
}

// ==========================================
// 2. ADMIN FUNCTIONS
// ==========================================

function renderAdmins() {
    const tbody = document.getElementById('adminTableBody');
    if(!tbody) return;
    
    const admins = DB.getAdmins();
    tbody.innerHTML = '';

    admins.forEach(admin => {
        // ซ่อนรหัสผ่าน
        tbody.innerHTML += `
            <tr>
                <td class="ps-4 fw-bold text-primary">${admin.name}</td>
                <td><span class="badge bg-light text-dark border">${admin.user}</span></td>
                <td>
                    <div class="input-group input-group-sm" style="width: 150px;">
                        <input type="password" class="form-control border-0 bg-transparent" value="${admin.pass}" id="pass_${admin.id}" readonly>
                        <button class="btn btn-link text-secondary" onclick="togglePass('${admin.id}')">
                            <i class="bi bi-eye-fill" id="eye_${admin.id}"></i>
                        </button>
                    </div>
                </td>
                <td>${admin.role}</td>
                <td class="text-end pe-4">
                    <button onclick="deleteAdmin('${admin.id}')" class="btn btn-sm btn-outline-danger" ${admin.id === 'a1' ? 'disabled' : ''}>
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
}

function openAdminModal() {
    document.getElementById('adminId').value = '';
    document.getElementById('adminName').value = '';
    document.getElementById('adminUser').value = '';
    document.getElementById('adminPass').value = '';
    if(adminModal) adminModal.show();
}

function saveAdmin() {
    const name = document.getElementById('adminName').value.trim();
    const user = document.getElementById('adminUser').value.trim();
    const pass = document.getElementById('adminPass').value.trim();
    const role = document.getElementById('adminRole').value;

    if(!name || !user || !pass) {
        alert('กรุณากรอกข้อมูลให้ครบถ้วน');
        return;
    }

    let admins = DB.getAdmins();
    const existing = admins.find(a => a.user === user);
    if (existing) {
        alert("Username นี้มีอยู่ในระบบแล้ว");
        return;
    }

    const newId = 'a' + Date.now();
    admins.push({ id: newId, name, user, pass, role });
    DB.saveAdmins(admins);
    
    if(adminModal) adminModal.hide();
    renderAdmins();
    alert("✅ เพิ่มผู้ดูแลเรียบร้อย");
}

function deleteAdmin(id) {
    if (id === 'a1') {
        alert("ไม่สามารถลบ Super Admin หลักได้");
        return;
    }
    if(confirm('ยืนยันลบผู้ดูแลท่านนี้?')) {
        let admins = DB.getAdmins().filter(a => a.id != id);
        DB.saveAdmins(admins);
        renderAdmins();
    }
}

function togglePass(id) {
    const input = document.getElementById(`pass_${id}`);
    const icon = document.getElementById(`eye_${id}`);
    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove('bi-eye-fill');
        icon.classList.add('bi-eye-slash-fill');
    } else {
        input.type = "password";
        icon.classList.remove('bi-eye-slash-fill');
        icon.classList.add('bi-eye-fill');
    }
}