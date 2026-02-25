// timer.js - Django Integrated Version (Light & Clean Theme)

let timerInterval; 
let startTime; // เก็บเวลาเริ่มใช้งานที่ได้มาจาก Backend หรือตอนโหลดหน้า
let forceEndTime = null; // สำหรับกรณีจองเวลา (ถ้ามีในอนาคต)

document.addEventListener('DOMContentLoaded', () => {
    // 1. กำหนดเวลาเริ่มต้นจากการโหลดหน้า
    startTime = Date.now(); 

    // 2. ดึงชื่อผู้ใช้จาก Session Storage (ที่เซฟไว้ตอน Check-in) มาแสดง
    const savedUser = sessionStorage.getItem('cklab_user_name');
    const userNameDisplay = document.getElementById('userNameDisplay');
    
    if (userNameDisplay) {
        if (savedUser && userNameDisplay.innerText.includes('กำลังโหลด')) {
            userNameDisplay.innerText = savedUser;
        } else if (!savedUser && userNameDisplay.innerText.includes('กำลังโหลด')) {
            userNameDisplay.innerText = 'ผู้ใช้งานระบบ Kiosk';
        }
    }
    
    // 3. อัปเดตการแสดงผลชื่อเครื่องและ Software 
    // ใช้ค่า PC_ID ที่ได้มาจาก Django Context 
    const pcIdDisplay = typeof PC_ID !== 'undefined' ? PC_ID : '??';
    
    // ค่าเริ่มต้น: General Use 
    let labelText = "General Use";

    // อัปเดต HTML: นำจุดสีเขียวกลับมา และเอา text-white ออกเพื่อไม่ให้ตัวหนังสือล่องหน
    const pcNameEl = document.getElementById('pcNameDisplay');
    if (pcNameEl) {
        pcNameEl.innerHTML = `
            <span class="status-indicator bg-success" style="width: 12px; height: 12px; margin-right: 8px;"></span>
            Station: ${pcIdDisplay} 
            <span class="text-muted fw-normal mx-2">|</span> 
            <span class="fw-normal" style="letter-spacing: 0.5px;">${labelText}</span>
        `;
    }
    
    // 4. เริ่มจับเวลา
    setupUnlimitedMode();
});

function setupUnlimitedMode() {
    console.log("Mode: Normal Timer (Elapsed)");
    const label = document.getElementById('timerLabel');
    if(label) label.innerText = "ระยะเวลาที่ใช้งาน (Usage Time)";
    
    updateTimer(); 
    if(timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(updateTimer, 1000); 
    
    // เช็คสถานะกับ Backend ทุก 5 วินาที เผื่อ Admin สั่งเตะออก
    setInterval(syncWithAdminUpdates, 5000);
}

function updateTimer() {
    const now = Date.now();
    let diff = now - startTime;
    if (diff < 0) diff = 0;
    
    const timerDisplay = document.getElementById('timerDisplay');
    if(timerDisplay) {
        timerDisplay.innerText = formatTime(diff);
        // เอาการเติม text-white ออกไป เพราะ CSS ธีมใหม่เราบังคับให้เป็นสีน้ำเงินเข้มแล้ว
        timerDisplay.classList.remove('text-danger', 'fw-bold'); 
    }
}

async function syncWithAdminUpdates() {
    if (typeof PC_ID === 'undefined' || !PC_ID) return;

    try {
        const response = await fetch(`/kiosk/api/status/${PC_ID}/`);
        if (!response.ok) return;

        const data = await response.json();

        // หากสถานะเครื่องกลายเป็น AVAILABLE หรือ MAINTENANCE แปลว่าแอดมินสั่งเคลียร์เครื่องแล้ว
        if (data.status === 'AVAILABLE' || data.status === 'MAINTENANCE') {
            alert("⚠️ Admin ได้ทำการรีเซ็ตเครื่องหรือเช็คเอาท์ให้คุณแล้ว");
            window.location.href = `/kiosk/?pc=${PC_ID}`; // กลับหน้าแรกทันที (ไม่ผ่าน feedback)
            return;
        }

    } catch (error) {
        console.error("Sync error:", error);
    }
}

function formatTime(ms) {
    const h = Math.floor(ms / 3600000).toString().padStart(2, '0');
    const m = Math.floor((ms % 3600000) / 60000).toString().padStart(2, '0');
    const s = Math.floor((ms % 60000) / 1000).toString().padStart(2, '0');
    return `${h}:${m}:${s}`;
}

function showAlert(msg) {
    const box = document.getElementById('alertBox');
    const txt = document.getElementById('alertMsg');
    if(box && txt) {
        box.classList.remove('d-none');
        txt.innerText = msg;
    }
}

function hideAlert() {
    const box = document.getElementById('alertBox');
    if(box) box.classList.add('d-none');
}

function doCheckout(isAuto = false) {
    if (!isAuto && !confirm('คุณต้องการเลิกใช้งานและออกจากระบบใช่หรือไม่?')) return;
    if (timerInterval) clearInterval(timerInterval);

    // ป้องกันการกดปุ่มซ้ำรัวๆ
    const btn = document.querySelector('.btn-danger');
    if(btn) btn.disabled = true;

    // สั่งให้ Form ที่ครอบปุ่ม Checkout ไว้ ทำการ Submit ตัวเองไปยัง Django Backend (CheckoutView)
    const form = document.getElementById('checkoutForm');
    if (form) {
        form.submit();
    } else {
        alert("ไม่พบฟอร์มสำหรับ Checkout กรุณาติดต่อผู้ดูแลระบบ");
    }
}