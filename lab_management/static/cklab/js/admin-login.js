/* admin-login.js (Django Standard Submit Version) */

document.addEventListener('DOMContentLoaded', () => {
    
    // 1. ตั้งค่าลิงก์ "ย้อนกลับ" ให้เด้งไปหน้าเครื่องล่าสุด หรือ PC-01 (ค่าเริ่มต้น)
    const backLink = document.getElementById('backLink');
    if (backLink) {
        // ดึงค่าเครื่องล่าสุดจาก Session (ถ้าไม่มี ให้ใช้ 'PC-01')
        const savedPcId = sessionStorage.getItem('cklab_pc_id') || 'PC-01';
        
        // อัปเดตลิงก์ให้กลับไปยังหน้าเครื่องนั้นๆ โดยตรง
        backLink.href = `/?pc=${savedPcId}`; 
        
        // เปลี่ยนข้อความให้แสดงชื่อเครื่อง
        backLink.innerHTML = `<i class="bi bi-arrow-left me-1"></i>กลับไปหน้า Check-in (${savedPcId})`;
    }

    // 2. รองรับการกดปุ่ม Enter ที่ฟอร์มเพื่อ Login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault(); // ป้องกันการ Submit ซ้ำซ้อน
                doAdminLogin();     // เรียกฟังก์ชันตรวจสอบและส่งข้อมูล
            }
        });
    }
});

// --- ฟังก์ชัน Login หลัก ---
function doAdminLogin() {
    // 1. ดึง Element จาก HTML
    const userEl = document.getElementById('admUser');
    const passEl = document.getElementById('admPass');
    const loginForm = document.getElementById('loginForm');

    if (!userEl || !passEl || !loginForm) {
        console.error("Error: ไม่พบ Element ของฟอร์ม Login");
        return;
    }

    const username = userEl.value.trim();
    const password = passEl.value.trim();

    // 2. ตรวจสอบว่ากรอกข้อมูลครบหรือไม่
    if (!username || !password) {
        alert('กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ครบถ้วน');
        return;
    }

    // 3. กำหนดแอตทริบิวต์ name ให้ตรงกับที่ Django ต้องการ (เผื่อใน HTML ไม่ได้ใส่ไว้)
    userEl.name = "username";
    passEl.name = "password";

    // 4. สั่ง Submit ฟอร์ม เพื่อให้ Django LoginView รับช่วงต่อ
    loginForm.method = "POST";
    loginForm.submit();
}