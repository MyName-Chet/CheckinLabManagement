/* feedback.js - Django Integrated Version */

let currentRate = 5; // คะแนนที่ถูกเลือก

// ข้อความและสีบรรยายระดับคะแนน (ใช้ในการแสดงผล)
const RATING_TEXTS = {
    1: "ต้องปรับปรุง", 2: "พอใช้", 3: "ปานกลาง", 4: "ดี", 5: "ยอดเยี่ยม"
};
const RATING_COLORS = {
    1: "#dc3545", 2: "#dc3545", 3: "#ffc107", 4: "#28a745", 5: "#198754"
};

document.addEventListener('DOMContentLoaded', () => {
    // ล้างข้อมูล Session ใน LocalStorage (ถ้าเคยมีเก็บไว้ตอน Check-in แบบเดิม)
    if (typeof localStorage !== 'undefined') {
        localStorage.removeItem('cklab_session');
    }

    // 2. แสดงข้อมูลระยะเวลา (ถ้ามีในอนาคต สามารถส่งจาก Django เข้ามาใส่ได้)
    const durationDisplay = document.getElementById('durationDisplay');
    if (durationDisplay) {
        durationDisplay.textContent = `สิ้นสุดการใช้งาน`;
    }

    // 3. ตั้งค่าเริ่มต้นที่ 5 ดาว (Default)
    setRate(5);
});

// --- 1. ฟังก์ชันจัดการดาวและการให้คะแนน ---

function getStarElements() {
    return document.querySelectorAll('#starContainer span');
}

function setRate(rate) {
    currentRate = rate;
    
    // ✅ อัปเดตค่าไปยัง <input type="hidden" id="scoreValue"> เพื่อให้ Django รับค่าไปบันทึก
    const scoreInput = document.getElementById('scoreValue');
    if (scoreInput) scoreInput.value = rate;

    const stars = getStarElements();
    if (stars.length === 0) return;

    stars.forEach((star, index) => {
        star.classList.toggle('active', index < rate);
        star.classList.remove('hover-active');
    });
    updateRateText(rate);
}

function updateRateText(rate) {
    const txtElement = document.getElementById('rateText');
    if (txtElement) {
        txtElement.innerText = `${RATING_TEXTS[rate]} (${rate}/5)`;
        txtElement.style.color = RATING_COLORS[rate];
    }
}

function hoverStar(rate) {
    const stars = getStarElements();
    if (stars.length === 0) return;
    stars.forEach((star, index) => {
        star.classList.toggle('hover-active', index < rate);
    });
}

function resetHover() {
    const stars = getStarElements();
    if (stars.length === 0) return;
    stars.forEach(star => star.classList.remove('hover-active'));
}


// --- 3. ฟังก์ชันส่งข้อมูล (Submit) ---

function submitFeedback() {
    // ป้องกันการกดปุ่มซ้ำ
    const submitButton = document.querySelector('.btn-primary');
    if (submitButton) submitButton.disabled = true;

    try {
        const form = document.getElementById('feedbackForm');
        
        if (form) {
            // ถ้ามีตัวแปรจาก Django ให้แสดง Popup แจ้งเตือนสวยๆ ก่อน Redirect ผ่าน Form Submit
            alert(`✅ บันทึกข้อมูลเรียบร้อย (คะแนน: ${currentRate}/5)\nขอบคุณที่ใช้บริการห้องปฏิบัติการคอมพิวเตอร์ครับ`);
            
            // ให้ Form Submit ไปที่ URL ปัจจุบัน ซึ่งจะไปเข้า `post()` ของ FeedbackView ใน Django
            form.submit(); 
        } else {
            throw new Error("ไม่พบฟอร์มส่งข้อมูล (#feedbackForm)");
        }

    } catch (error) {
        console.error("Feedback Submission Error:", error);
        alert("❌ เกิดข้อผิดพลาดในการส่งข้อมูล (โปรดแจ้งเจ้าหน้าที่: " + error.message + ")");
        if (submitButton) submitButton.disabled = false;
    }
}

// ✅ ฟังก์ชันแสดงรายการข้อเสนอแนะ (เก็บไว้เผื่อนำไปใช้หน้า Dashboard/Admin)
function renderFeedbackComments(logs) {
    const container = document.getElementById('feedbackCommentList');
    const countBadge = document.getElementById('commentCount');
    if (!container) return;

    // 1. กรองเฉพาะคนที่มีคอมเมนต์
    const comments = logs.filter(log => log.comment && log.comment.trim() !== "");

    // อัปเดตตัวเลข
    if(countBadge) countBadge.innerText = comments.length;

    // ว่างเปล่า
    if (comments.length === 0) {
        container.innerHTML = `
            <div class="d-flex flex-column align-items-center justify-content-center h-100 text-muted mt-5">
                <i class="bi bi-chat-square-heart fs-1 opacity-25 mb-2"></i>
                <p class="small">ยังไม่มีข้อเสนอแนะในขณะนี้</p>
            </div>`;
        return;
    }

    // 2. เรียงลำดับ (ใหม่สุดขึ้นก่อน)
    const sortedComments = comments.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    // 3. สร้าง HTML การ์ดสวยๆ
    container.innerHTML = sortedComments.map(log => {
        const score = parseInt(log.satisfactionScore) || 0;
        
        // ดาว (Star Rating)
        let stars = '';
        for(let i=1; i<=5; i++) {
            stars += i <= score ? '<i class="bi bi-star-fill text-warning"></i>' : '<i class="bi bi-star text-muted opacity-25"></i>';
        }

        const dateObj = new Date(log.timestamp);
        const dateStr = dateObj.toLocaleDateString('th-TH', { day: 'numeric', month: 'short' });
        const timeStr = dateObj.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' });
        const user = log.userName || 'Unknown';
        const role = log.userRole === 'student' ? 'นักศึกษา' : (log.userRole === 'staff' ? 'บุคลากร' : 'Guest');
        
        // สีตามคะแนน (Sentiment Color)
        let borderColor = '#dc3545'; // แดง (1-2)
        let sentimentIcon = 'bi-emoji-frown';
        let avatarColor = 'bg-danger';

        if (score >= 4) { 
            borderColor = '#198754'; // เขียว (4-5)
            sentimentIcon = 'bi-emoji-smile';
            avatarColor = 'bg-success';
        } else if (score === 3) {
            borderColor = '#ffc107'; // เหลือง (3)
            sentimentIcon = 'bi-emoji-neutral';
            avatarColor = 'bg-warning text-dark';
        }

        // Avatar (ตัวอักษรแรกของชื่อ)
        const initial = user.charAt(0).toUpperCase();

        return `
            <div class="card feedback-item border-0 shadow-sm mb-2" style="border-left: 5px solid ${borderColor} !important;">
                <div class="card-body p-3">
                    <div class="d-flex align-items-start">
                        <div class="avatar-circle ${avatarColor} bg-opacity-75 shadow-sm me-3 flex-shrink-0">
                            ${initial}
                        </div>
                        
                        <div class="flex-grow-1">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <div>
                                    <span class="fw-bold text-dark" style="font-size: 0.95rem;">${user}</span>
                                    <span class="badge bg-light text-secondary border ms-1 fw-normal" style="font-size: 0.7rem;">${role}</span>
                                </div>
                                <div class="small" style="font-size: 0.75rem;">${stars}</div>
                            </div>
                            
                            <p class="mb-2 text-secondary" style="font-size: 0.9rem; line-height: 1.5;">
                                "${log.comment}"
                            </p>
                            
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted" style="font-size: 0.75rem;">
                                    <i class="bi bi-pc-display me-1"></i>PC-${log.pcId}
                                </small>
                                <small class="text-muted" style="font-size: 0.75rem;">
                                    <i class="bi bi-clock me-1"></i>${dateStr} ${timeStr}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}