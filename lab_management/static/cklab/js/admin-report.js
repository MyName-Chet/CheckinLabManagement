/* admin-report.js (Django Integration Version - Part 1) */

// --- Global Variables ---
let monthlyFacultyChartInstance, monthlyOrgChartInstance;
let pieChartInstance, pcAvgChartInstance, topSoftwareChartInstance;
let allLogs = [];
let lastLogCount = 0;

// ✅ Pagination Variables
let currentPage = 1;
let rowsPerPage = 10;
let filteredLogsGlobal = []; 

// --- Master Lists ---
const FACULTY_LIST = [
    "คณะวิทยาศาสตร์", "คณะเกษตรศาสตร์", "คณะวิศวกรรมศาสตร์", "คณะศิลปศาสตร์", 
    "คณะเภสัชศาสตร์", "คณะบริหารศาสตร์", "คณะพยาบาลศาสตร์", "วิทยาลัยแพทยศาสตร์และการสาธารณสุข", 
    "คณะศิลปประยุกต์และสถาปัตยกรรมศาสตร์", "คณะนิติศาสตร์", "คณะรัฐศาสตร์", "คณะศึกษาศาสตร์"
];

const ORG_LIST = [
    "สำนักคอมพิวเตอร์และเครือข่าย", "สำนักบริหารทรัพย์สินและสิทธิประโยชน์", "สำนักวิทยบริการ", 
    "กองกลาง", "กองแผนงาน", "กองคลัง", "กองบริการการศึกษา", "กองการเจ้าหน้าที่", 
    "สำนักงานส่งเสริมและบริหารงานวิจัย ฯ", "สำนักงานพัฒนานักศึกษา", "สำนักงานบริหารกายภาพและสิ่งแวดล้อม", 
    "สำนักงานวิเทศสัมพันธ์", "สำนักงานนิติการ / สำนักงานกฎหมาย", "สำนักงานตรวจสอบภายใน", 
    "สำนักงานรักษาความปลอดภัย", "สภาอาจารย์", "สหกรณ์ออมทรัพย์มหาวิทยาลัยอุบลราชธานี", 
    "อุทยานวิทยาศาสตร์มหาวิทยาลัยอุบลราชธานี", "ศูนย์การจัดการความรู้ (KM)", 
    "ศูนย์การเรียนรู้และพัฒนา \"งา\" เชิงเกษตรอุตสาหกรรมครัวเรือนแบบยั่งยืน", 
    "สถานปฏิบัติการโรงแรมฯ (U-Place)", "ศูนย์วิจัยสังคมอนุภาคลุ่มน้ำโขง ฯ", 
    "ศูนย์เครื่องมือวิทยาศาสตร์", "โรงพิมพ์มหาวิทยาลัยอุบลราชธานี"
];

let distributionBarInstance = null;
let dailyTrendLineInstance = null;

// ==========================================
// 🚀 DJANGO API INTEGRATION
// ==========================================

async function fetchLogsFromDjango() {
    try {
        const response = await fetch('/admin-portal/report/api/logs/'); 
        if (!response.ok) return [];
        
        const data = await response.json();
        
        return data.logs.map(log => {
            const start = new Date(log.start_time);
            const end = log.end_time ? new Date(log.end_time) : new Date();
            const durationMs = end - start;
            const durationMinutes = log.end_time ? Math.floor(durationMs / 60000) : 0;
            
            const swList = log.Software ? log.Software.split(';').map(s => s.trim()) : [];
            const isAI = swList.some(s => s.toLowerCase().includes('gpt') || s.toLowerCase().includes('claude') || s.toLowerCase().includes('ai'));

            return {
                id: log.id,
                userId: log.user_id,
                userName: log.user_name,
                userRole: log.user_type, 
                userFaculty: log.department || 'ไม่ระบุ',
                userLevel: 'ปริญญาตรี', 
                userYear: log.user_year || '-',
                pcId: log.computer ? log.computer.replace('PC-', '') : '?',
                durationMinutes: durationMinutes,
                usedSoftware: swList,
                isAIUsed: isAI,
                timestamp: log.end_time || log.start_time,
                startTime: log.start_time,
                action: log.end_time ? 'END_SESSION' : 'IN_USE'
            };
        });
    } catch (error) {
        console.error("Error fetching logs:", error);
        return [];
    }
}

// --- Initialization ---
document.addEventListener('DOMContentLoaded', async () => {
    initFilters();      
    initDateInputs();   
    
    allLogs = await fetchLogsFromDjango();
    lastLogCount = allLogs.length; 
    
    if (typeof renderLifetimeStats === 'function') {
        renderLifetimeStats();
    } else {
        console.warn("renderLifetimeStats not found, skipping.");
    }
    
    applyFilters(); 
    setInterval(checkForUpdates, 10000); 
});

async function checkForUpdates() {
    const currentLogs = await fetchLogsFromDjango();
    if (currentLogs.length !== lastLogCount) {
        allLogs = currentLogs;
        lastLogCount = currentLogs.length;
        applyFilters(); 
        if (typeof renderLifetimeStats === 'function') renderLifetimeStats();
    }
}

// ==========================================
// 1. INIT UI COMPONENTS
// ==========================================

function initFilters() {
    const facContainer = document.getElementById('studentFacultyList');
    if (facContainer) {
        facContainer.innerHTML = FACULTY_LIST.map((fac, index) => `
            <div class="form-check">
                <input class="form-check-input fac-check" type="checkbox" value="${fac}" id="fac_${index}" checked>
                <label class="form-check-label small" for="fac_${index}">${fac}</label>
            </div>
        `).join('');
    }

    const orgContainer = document.getElementById('staffOrgList');
    if (orgContainer) {
        const ALL_STAFF_DEPTS = [...FACULTY_LIST, ...ORG_LIST];
        orgContainer.innerHTML = ALL_STAFF_DEPTS.map((org, index) => `
            <div class="form-check">
                <input class="form-check-input org-check" type="checkbox" value="${org}" id="org_staff_${index}" checked>
                <label class="form-check-label small" for="org_staff_${index}">${org}</label>
            </div>
        `).join('');
    }

    const yearStart = document.getElementById('yearStart');
    const yearEnd = document.getElementById('yearEnd');
    const qYear = document.getElementById('quarterYear'); // 🌟 dropdown สำหรับปีไตรมาส

    if (yearStart && yearEnd) {
        const currentYear = new Date().getFullYear() + 543;
        for (let y = currentYear; y >= currentYear - 5; y--) {
            const yValue = y - 543;
            yearStart.innerHTML += `<option value="${yValue}">${y}</option>`;
            yearEnd.innerHTML += `<option value="${yValue}">${y}</option>`;
            if(qYear) qYear.innerHTML += `<option value="${yValue}">${y}</option>`;
        }
        yearStart.value = currentYear - 543;
        yearEnd.value = currentYear - 543;
        if(qYear) qYear.value = currentYear - 543;
    }

    updateQuarterLabels(); // อัปเดต Label ไตรมาสตอนเริ่ม
}

function initDateInputs() {
    const today = new Date();
    const dStart = document.getElementById('dateStart');
    const dEnd = document.getElementById('dateEnd');
    if (dEnd) dEnd.valueAsDate = today;
    if (dStart) {
        const lastMonth = new Date();
        lastMonth.setDate(lastMonth.getDate() - 30);
        dStart.valueAsDate = lastMonth;
    }
    const mStr = today.toISOString().slice(0, 7);
    const mStart = document.getElementById('monthStart');
    const mEnd = document.getElementById('monthEnd');
    if (mStart) mStart.value = mStr;
    if (mEnd) mEnd.value = mStr;
}

// 🌟 ฟังก์ชันสำหรับอัปเดต Label ของไตรมาส ให้มีปี พ.ศ. กำกับ
function updateQuarterLabels() {
    const qSelect = document.getElementById('quarterSelect');
    const qYearEl = document.getElementById('quarterYear');
    if (!qSelect || !qYearEl) return;

    const currentThaiYear = parseInt(qYearEl.options[qYearEl.selectedIndex].text);
    const nextThaiYear = currentThaiYear + 1;

    qSelect.innerHTML = `
        <option value="1">ไตรมาส 1 (ต.ค.-ธ.ค. ${currentThaiYear})</option>
        <option value="2">ไตรมาส 2 (ม.ค.-มี.ค. ${nextThaiYear})</option>
        <option value="3">ไตรมาส 3 (เม.ย.-มิ.ย. ${nextThaiYear})</option>
        <option value="4">ไตรมาส 4 (ก.ค.-ก.ย. ${nextThaiYear})</option>
    `;
}

// ==========================================
// 2. UI INTERACTION
// ==========================================

function toggleFilterMode() {
    const modeEl = document.querySelector('input[name="userTypeOption"]:checked');
    if (!modeEl) return;
    const mode = modeEl.value;

    ['student', 'staff', 'external', 'guest', 'all'].forEach(m => {
        const el = document.getElementById(`filter-${m}-section`);
        if(el) el.classList.add('d-none');
    });

    const targetEl = document.getElementById(`filter-${mode}-section`);
    if(targetEl) {
        targetEl.classList.remove('d-none');
    } else {
        const fallback = document.getElementById('filter-all-section');
        if(fallback) fallback.classList.remove('d-none');
    }
}

function toggleTimeInputs() {
    const typeEl = document.getElementById('timeFilterType');
    if (!typeEl) return;
    const type = typeEl.value;

    ['daily', 'monthly', 'quarterly', 'yearly'].forEach(t => {
        const el = document.getElementById(`input-${t}`);
        if (el) el.classList.add('d-none');
    });
    const target = document.getElementById(`input-${type}`);
    if (target) target.classList.remove('d-none');
}

function toggleCheckAll(containerId) {
    const checkboxes = document.querySelectorAll(`#${containerId} input[type="checkbox"]`);
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    checkboxes.forEach(cb => cb.checked = !allChecked);
}

function getCheckedValues(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    return Array.from(container.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value);
}

function toggleStudentYearInputs() {
    const levelSelect = document.getElementById('filterEduLevel');
    const yearContainer = document.getElementById('filterYearContainer');
    
    if (levelSelect && yearContainer) {
        if (levelSelect.value === 'ปริญญาตรี') {
            yearContainer.classList.remove('d-none'); 
        } else {
            yearContainer.classList.add('d-none'); 
            document.getElementById('filterStudentYear').value = 'all'; 
        }
    }
}

// ==========================================
// 3. CORE LOGIC (FILTER)
// ==========================================

function generateReport() {
    currentPage = 1;
    applyFilters(); 
}

function applyFilters() { 
    const allStatsLogs = allLogs.filter(l => l.action === 'END_SESSION');

    const userModeEl = document.querySelector('input[name="userTypeOption"]:checked');
    const userMode = userModeEl ? userModeEl.value : 'all';
    const timeMode = document.getElementById('timeFilterType').value;
    const selectedFaculties = getCheckedValues('studentFacultyList');
    const selectedOrgs = getCheckedValues('staffOrgList');

    let isSingleYear = false;
    if (timeMode === 'yearly') {
        const yStart = document.getElementById('yearStart').value;
        const yEnd = document.getElementById('yearEnd').value;
        if (yStart === yEnd) isSingleYear = true;
    }

    let filteredLogs = allStatsLogs.filter(log => {
        const logDate = new Date(log.startTime || log.timestamp);
        const logFaculty = (log.userFaculty || "").trim();

        // 1. กรองเวลา
        if (timeMode === 'daily') {
            const start = new Date(document.getElementById('dateStart').value);
            const end = new Date(document.getElementById('dateEnd').value);
            if (!isNaN(start) && !isNaN(end)) {
                start.setHours(0,0,0,0); end.setHours(23,59,59,999);
                if (logDate < start || logDate > end) return false;
            }
        } else if (timeMode === 'monthly') {
            const mStart = new Date(document.getElementById('monthStart').value + "-01");
            const mEndParts = document.getElementById('monthEnd').value.split('-');
            const mEnd = new Date(mEndParts[0], mEndParts[1], 0, 23, 59, 59);
            if (logDate < mStart || logDate > mEnd) return false;
        } else if (timeMode === 'yearly') {
            const yStart = parseInt(document.getElementById('yearStart').value);
            const yEnd = parseInt(document.getElementById('yearEnd').value);
            const logYear = logDate.getFullYear(); 
            if (logYear < yStart || logYear > yEnd) return false;
        } else if (timeMode === 'quarterly') {
            // 🌟 กรองแบบรายไตรมาส (ปีงบประมาณไทย ตุลาคมเป็น Q1)
            const qYear = parseInt(document.getElementById('quarterYear').value);
            const qVal = parseInt(document.getElementById('quarterSelect').value);
            let qStart, qEnd;
            if (qVal === 1) { qStart = new Date(qYear, 9, 1); qEnd = new Date(qYear, 11, 31, 23, 59, 59); } 
            else if (qVal === 2) { qStart = new Date(qYear + 1, 0, 1); qEnd = new Date(qYear + 1, 2, 31, 23, 59, 59); } 
            else if (qVal === 3) { qStart = new Date(qYear + 1, 3, 1); qEnd = new Date(qYear + 1, 5, 30, 23, 59, 59); } 
            else if (qVal === 4) { qStart = new Date(qYear + 1, 6, 1); qEnd = new Date(qYear + 1, 8, 30, 23, 59, 59); }
            if (logDate < qStart || logDate > qEnd) return false;
        }

        // 2. กรองประเภทผู้ใช้ 
        const role = (log.userRole || '').toLowerCase();
        
        if (userMode === 'student') {
            if (!role.includes('student') && !role.includes('นักศึกษา')) return false;
            const isFacultyMatch = selectedFaculties.some(fac => fac.trim() === logFaculty);
            if (!isFacultyMatch) return false;

            const filterLevel = document.getElementById('filterEduLevel').value;
            const filterYear = document.getElementById('filterStudentYear').value;
            const userLevel = (log.userLevel || "").toString().trim();
            const userYear = (log.userYear || "").toString().trim();

            if (filterLevel !== 'all') {
                if (userLevel !== filterLevel) return false;
                if (filterLevel === 'ปริญญาตรี' && filterYear !== 'all') {
                    if (userYear !== filterYear) return false;
                }
            }
        } 
        else if (userMode === 'staff') {
            const staffKeywords = ['staff', 'admin', 'teacher', 'อาจารย์', 'บุคลากร'];
            if (!staffKeywords.some(kw => role.includes(kw))) return false;
            
            const currentLogFaculty = (log.userFaculty || "").replace(/["\\]/g, "").trim();
            return selectedOrgs.some(org => {
                const selectedOrgClean = org.replace(/["\\]/g, "").trim();
                return currentLogFaculty.includes(selectedOrgClean) || selectedOrgClean.includes(currentLogFaculty);
            });
        }
        else if (userMode === 'external' || userMode === 'guest') {
            if (!role.includes('guest') && !role.includes('external') && !role.includes('ภายนอก')) return false;
        }
        
        return true;
    });

    let distributionData = {};
    const timeChartData = {};

    filteredLogs.forEach(l => {
        let distLabel = l.userFaculty || 'ไม่ระบุ';
        const roleCheck = (l.userRole || '').toLowerCase();
        
        if (userMode === 'all') {
            if (roleCheck.includes('student') || roleCheck.includes('นักศึกษา')) distLabel = "นักศึกษา";
            else if (roleCheck.includes('staff') || roleCheck.includes('admin') || roleCheck.includes('teacher') || roleCheck.includes('อาจารย์') || roleCheck.includes('บุคลากร')) distLabel = "บุคลากร";
            else distLabel = "บุคคลภายนอก";
        }
        distributionData[distLabel] = (distributionData[distLabel] || 0) + 1;

        const dateObj = new Date(l.startTime || l.timestamp);
        let timeLabel;

        if (timeMode === 'daily' || timeMode === 'monthly') {
            timeLabel = dateObj.toLocaleDateString('th-TH', { day: 'numeric', month: 'short' });
        } else if (timeMode === 'yearly') {
            if (isSingleYear) {
                timeLabel = dateObj.toLocaleDateString('th-TH', { month: 'long' });
            } else {
                timeLabel = (dateObj.getFullYear() + 543).toString();
            }
        } else if (timeMode === 'quarterly') {
            const logMonth = dateObj.getMonth();
            if (logMonth >= 9 && logMonth <= 11) timeLabel = "Q1 (ต.ค.-ธ.ค.)";
            else if (logMonth >= 0 && logMonth <= 2) timeLabel = "Q2 (ม.ค.-มี.ค.)";
            else if (logMonth >= 3 && logMonth <= 5) timeLabel = "Q3 (เม.ย.-มิ.ย.)";
            else if (logMonth >= 6 && logMonth <= 8) timeLabel = "Q4 (ก.ค.-ก.ย.)";
        }
        timeChartData[timeLabel] = (timeChartData[timeLabel] || 0) + 1;
    });

    updateSummaryCards(filteredLogs);
    drawDistributionBarChart(distributionData);
    drawDailyTrendLineChart(timeChartData, timeMode, isSingleYear);

    const globalChartData = processLogsForCharts(filteredLogs, timeMode);
    if (topSoftwareChartInstance) topSoftwareChartInstance.destroy();
    topSoftwareChartInstance = drawTopSoftwareChart(globalChartData.softwareStats);
    
    if (pieChartInstance) pieChartInstance.destroy();
    pieChartInstance = drawAIUsagePieChart(globalChartData.aiUsageData);
    
    renderLogHistory(filteredLogs);
}

function updateSummaryCards(data) {
    const uniqueUsers = new Set(data.map(log => log.userId)).size;
    const sessionCount = data.length;
    let totalMinutes = 0;
    data.forEach(log => { totalMinutes += (log.durationMinutes || 0); });
    const totalHours = (totalMinutes / 60).toFixed(1);

    animateValue("resultUserCount", 0, uniqueUsers, 500); 
    animateValue("resultSessionCount", 0, sessionCount, 500);
    animateValue("resultTotalHours", 0, parseFloat(totalHours), 500);
}

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    if(!obj) return;
    obj.innerHTML = end.toLocaleString(); 
}

// ==========================================
// 4. CHART PROCESSING
// ==========================================

function processLogsForCharts(logs, mode) {
    const result = {
        monthlyFacultyData: {}, monthlyOrgData: {}, aiUsageData: { ai: 0, nonAI: 0 },
        pcAvgTimeData: [],
        softwareStats: {}, quickStats: { topPC: { name: '-', value: 0 }, avgTime: { hours: 0, minutes: 0 } }
    };
    
    const pcUsageMap = new Map();

    logs.forEach(log => {
        if (log.isAIUsed) result.aiUsageData.ai++; else result.aiUsageData.nonAI++;

        if (Array.isArray(log.usedSoftware)) {
            log.usedSoftware.forEach(sw => {
                const name = sw.split('(')[0].trim();
                result.softwareStats[name] = (result.softwareStats[name] || 0) + 1;
            });
        }

        const pcId = String(log.pcId);
        const duration = log.durationMinutes || 0;
        
        if (!pcUsageMap.has(pcId)) {
            pcUsageMap.set(pcId, { total: 0, count: 0 });
        }
        pcUsageMap.get(pcId).total += duration;
        pcUsageMap.get(pcId).count++;
    });

    return result;
}

// ==========================================
// 5. CHART DRAWING FUNCTIONS
// ==========================================

function drawDistributionBarChart(data) {
    const ctx = document.getElementById('distributionBarChart');
    if (!ctx) return;
    if (distributionBarInstance) distributionBarInstance.destroy();

    const customOrder = { "นักศึกษา": 1, "บุคลากร": 2, "บุคคลภายนอก": 3 };
    
    const sortedData = Object.entries(data).sort((a, b) => {
        const orderA = customOrder[a[0]] || 99;
        const orderB = customOrder[b[0]] || 99;
        if (orderA !== orderB) return orderA - orderB;
        return b[1] - a[1];
    });

    distributionBarInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedData.map(x => x[0]),
            datasets: [{
                label: 'จำนวนครั้ง',
                data: sortedData.map(x => Math.floor(x[1])),
                backgroundColor: '#1d73f2',
                borderRadius: 4,
                categoryPercentage: 0.3, 
                barPercentage: 0.5,
                maxBarThickness: 35
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1, precision: 0, font: { family: "'Prompt', sans-serif" } }, grid: { color: '#f0f0f0', drawBorder: true } },
                x: { grid: { display: false }, ticks: { font: { family: "'Prompt', sans-serif", size: 12 }, color: '#666' } }
            },
            plugins: { legend: { display: false }, tooltip: { bodyFont: { family: "'Prompt', sans-serif" } } }
        }
    });
}

function drawDailyTrendLineChart(dailyData, timeMode, isSingleYear = false) {
    const ctx = document.getElementById('dailyTrendLineChart');
    if (!ctx) return;
    if (dailyTrendLineInstance) dailyTrendLineInstance.destroy();

    let labels = [];
    let dataPoints = [];

    if (timeMode === 'yearly') {
        if (isSingleYear) {
            labels = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"];
            dataPoints = labels.map(month => dailyData[month] || 0);
        } else {
            const yStart = parseInt(document.getElementById('yearStart').value); 
            const yEnd = parseInt(document.getElementById('yearEnd').value);     
            for (let y = yStart; y <= yEnd; y++) {
                const bYear = y + 543; 
                const key = bYear.toString();
                labels.push(key); 
                dataPoints.push(dailyData[key] || 0); 
            }
        }
    } 
    // 🌟 เพิ่มเงื่อนไขเรียงลำดับให้กราฟแสดง Q1, Q2, Q3, Q4 ถูกต้อง
    else if (timeMode === 'quarterly') {
        labels = ["Q1 (ต.ค.-ธ.ค.)", "Q2 (ม.ค.-มี.ค.)", "Q3 (เม.ย.-มิ.ย.)", "Q4 (ก.ค.-ก.ย.)"];
        dataPoints = labels.map(q => dailyData[q] || 0);
    }
    else if (timeMode === 'daily' || timeMode === 'monthly') {
        let startD, endD;
        if (timeMode === 'daily') {
            startD = new Date(document.getElementById('dateStart').value);
            endD = new Date(document.getElementById('dateEnd').value);
        } else {
            const mStartVal = document.getElementById('monthStart').value;
            const mEndVal = document.getElementById('monthEnd').value;
            startD = new Date(mStartVal + "-01");
            const parts = mEndVal.split('-');
            endD = new Date(parts[0], parts[1], 0);
        }

        if (startD && endD && !isNaN(startD) && !isNaN(endD)) {
            let curr = new Date(startD);
            while (curr <= endD) {
                const dateStr = curr.toLocaleDateString('th-TH', { day: 'numeric', month: 'short' });
                labels.push(dateStr);
                dataPoints.push(dailyData[dateStr] || 0);
                curr.setDate(curr.getDate() + 1);
            }
        }
    } 
    else {
        labels = Object.keys(dailyData);
        dataPoints = labels.map(d => dailyData[d]);
    }

    dailyTrendLineInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'จำนวนครั้งการใช้งาน',
                data: dataPoints,
                borderColor: '#1d73f2',
                backgroundColor: 'rgba(29, 115, 242, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0, 
                pointBackgroundColor: '#1d73f2',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 } },
                x: { grid: { display: true, color: '#f0f0f0' }, ticks: { font: { family: "'Prompt', sans-serif", size: 10 } } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function drawTopSoftwareChart(data) {
    const ctx = document.getElementById('topSoftwareChart');
    if(!ctx) return;
    const existingChart = Chart.getChart(ctx);
    if (existingChart) existingChart.destroy();

    const sorted = Object.entries(data).sort((a,b) => b[1] - a[1]).slice(0, 10);
    const grandTotal = Object.values(data).reduce((acc, val) => acc + val, 0);

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 400, 0);
    gradient.addColorStop(0, '#4e73df'); gradient.addColorStop(1, '#36b9cc');

    return new Chart(ctx, {
        type: 'bar',
        data: { 
            labels: sorted.map(x=>x[0]), 
            datasets: [{ 
                label: 'จำนวนการใช้งาน', 
                data: sorted.map(x=>x[1]), 
                backgroundColor: gradient, 
                borderRadius: 10, 
                barPercentage: 0.6 
            }] 
        },
        plugins: [{
            id: 'customBarLabels',
            afterDatasetsDraw(chart) {
                const { ctx } = chart;
                ctx.save();
                ctx.font = "bold 12px 'Prompt', sans-serif"; 
                ctx.fillStyle = '#666'; 
                ctx.textBaseline = 'middle';
                
                chart.getDatasetMeta(0).data.forEach((datapoint, index) => {
                    const value = sorted[index][1];
                    const percentage = grandTotal > 0 ? ((value / grandTotal) * 100).toFixed(1) + '%' : '0%';
                    ctx.fillText(percentage, datapoint.x + 5, datapoint.y);
                });
                ctx.restore();
            }
        }],
        options: { 
            indexAxis: 'y', 
            responsive: true, 
            maintainAspectRatio: false, 
            layout: { padding: { right: 45 } },
            plugins: { 
                legend: {display:false}, 
                tooltip: { 
                    callbacks: { 
                        label: (c) => {
                            const val = c.raw;
                            const per = grandTotal > 0 ? ((val/grandTotal)*100).toFixed(1) : 0;
                            return ` ${val} ครั้ง (${per}%)`;
                        } 
                    } 
                } 
            }, 
            scales: { 
                x: { beginAtZero: true, grid: { display: false }, ticks: { font: { family: "'Prompt', sans-serif" } } }, 
                y: { grid: {display:false}, ticks: { font: { family: "'Prompt', sans-serif", weight: '500' } } } 
            } 
        }
    });
}

function drawAIUsagePieChart(d) { 
    const total = d.ai + d.nonAI;
    const toStrikethrough = (text) => text.split('').map(char => char + '\u0336').join('');

    return new Chart(document.getElementById('aiUsagePieChart'), { 
        type: 'doughnut', 
        data: { 
            labels: ['AI Tools', 'General Use'], 
            datasets: [{ 
                data: [d.ai, d.nonAI], 
                backgroundColor: ['#4e73df', '#e2e6ea'], 
                borderWidth: 0, 
                hoverOffset: 4 
            }] 
        }, 
        options: { 
            responsive: true, 
            maintainAspectRatio: false, 
            layout: { padding: { top: 10, bottom: 10, left: 10, right: 20 } },
            plugins: { 
                legend: { 
                    position: 'right', 
                    align: 'start',    
                    labels: { 
                        usePointStyle: true, 
                        font: { family: "'Prompt', sans-serif", size: 12 },
                        padding: 20,
                        boxWidth: 10,
                        generateLabels: (chart) => {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map((label, i) => {
                                    const value = data.datasets[0].data[i];
                                    const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                    const color = data.datasets[0].backgroundColor[i];
                                    const isHidden = !chart.getDataVisibility(i);
                                    let textLabel = `${label} (${percentage}%)`;
                                    if (isHidden) textLabel = toStrikethrough(textLabel);

                                    return {
                                        text: textLabel,
                                        fillStyle: color, 
                                        strokeStyle: color,
                                        lineWidth: 0,
                                        hidden: isHidden,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                onClick: (e, legendItem, legend) => {
                    const index = legendItem.index;
                    const ci = legend.chart;
                    if (ci.isDatasetVisible(0)) {
                        ci.toggleDataVisibility(index);
                        ci.update();
                    }
                }
            },
            tooltip: { 
                callbacks: { 
                    label: (context) => {
                        const value = context.raw;
                        const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                        return ` ${context.label}: ${value.toLocaleString()} ครั้ง (${percentage}%)`;
                    } 
                } 
            } 
        }, 
        cutout: '65%'
    }); 
}

// ==========================================
// 6. RENDER TABLES & HELPERS (PAGINATION FIXED)
// ==========================================

function renderLogHistory(logs) {
    filteredLogsGlobal = logs || [];
    
    const totalItems = filteredLogsGlobal.length;
    const tbody = document.getElementById('logHistoryTableBody');
    if (!tbody) return;

    if (totalItems === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted py-5"><i class="bi bi-inbox fs-1 d-block mb-2 opacity-25"></i>ไม่พบข้อมูลประวัติการใช้งาน</td></tr>`;
        updatePaginationControls(0, 0, 0);
        return;
    }

    if (typeof rowsPerPage === 'undefined') window.rowsPerPage = 10;
    if (typeof currentPage === 'undefined') window.currentPage = 1;

    const totalPages = Math.ceil(totalItems / rowsPerPage);
    if (currentPage > totalPages) currentPage = 1;
    if (currentPage < 1) currentPage = 1;

    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = Math.min(startIndex + rowsPerPage, totalItems);
    
    const currentLogs = filteredLogsGlobal
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(startIndex, endIndex);

    tbody.innerHTML = currentLogs.map((log, i) => {
        let dateStr = "-";
        let timeRangeStr = "-";

        if (log.timestamp) {
            const dateObj = new Date(log.timestamp);
            if (!isNaN(dateObj)) {
                dateStr = dateObj.toLocaleDateString('th-TH', { day: '2-digit', month: '2-digit', year: '2-digit' });
                
                if (log.startTime) {
                    const start = new Date(log.startTime);
                    const startStr = start.toLocaleTimeString('th-TH', {hour:'2-digit', minute:'2-digit'});
                    const endStr = dateObj.toLocaleTimeString('th-TH', {hour:'2-digit', minute:'2-digit'});
                    timeRangeStr = `${startStr} - ${endStr}`;
                } else {
                    timeRangeStr = dateObj.toLocaleTimeString('th-TH', {hour:'2-digit', minute:'2-digit'});
                }
            }
        }
        
        let roleBadge = '<span class="badge bg-secondary">Unknown</span>';
        const userRole = String(log.userRole || "").toLowerCase();

        if (userRole.includes('student') || userRole.includes('นักศึกษา')) {
            roleBadge = '<span class="badge bg-primary">นักศึกษา</span>';
        } else if (userRole.includes('staff') || userRole.includes('admin') || userRole.includes('teacher') || userRole.includes('อาจารย์') || userRole.includes('บุคลากร')) {
            roleBadge = '<span class="badge bg-success">บุคลากร/อาจารย์</span>';
        } else {
            roleBadge = '<span class="badge bg-dark">บุคคลภายนอก</span>';
        }

        let swTags = '-';
        if (log.usedSoftware && log.usedSoftware.length > 0) {
            swTags = log.usedSoftware.map(s => {
                if (s && s !== '-') return `<span class="badge bg-light text-dark border me-1 mb-1">${s}</span>`;
                return '';
            }).join('');
            if (!swTags) swTags = '-';
        }

        let facultyDisplay = log.userFaculty || '-';
        if ((userRole.includes('student') || userRole.includes('นักศึกษา')) && log.userYear && log.userYear !== '-') {
            facultyDisplay += ` <small class="text-muted">(ปี ${log.userYear})</small>`;
        }

        return `
            <tr>
                <td class="text-center text-muted small">${startIndex + i + 1}</td>
                <td class="fw-bold text-primary text-center">${log.userId || '-'}</td>
                <td>${log.userName || 'Unknown'}</td>
                <td><div class="d-flex flex-wrap justify-content-center">${swTags}</div></td>
                <td class="text-center">${dateStr}</td>
                <td class="text-center"><span class="badge bg-light text-dark border">${timeRangeStr}</span></td>
                <td>${facultyDisplay}</td>
                <td class="text-center">${roleBadge}</td>
                <td class="text-center"><span class="badge bg-dark bg-opacity-75">${log.pcId || '-'}</span></td>
            </tr>
        `;
    }).join('');

    updatePaginationControls(totalItems, startIndex + 1, endIndex);
}

function updatePaginationControls(totalItems, startItem, endItem) {
    const infoEl = document.getElementById('paginationInfo');
    const navEl = document.getElementById('paginationControls');
    
    if (infoEl) infoEl.innerText = `แสดง ${startItem} - ${endItem} จากทั้งหมด ${totalItems} รายการ`;
    if (!navEl) return;
    
    const totalPages = Math.ceil(totalItems / rowsPerPage);
    let html = '';

    html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link cursor-pointer" onclick="goToPage(${currentPage - 1})"><i class="bi bi-chevron-left"></i></a>
             </li>`;

    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
            html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                        <a class="page-link cursor-pointer" onclick="goToPage(${i})">${i}</a>
                      </li>`;
        } else if (i === currentPage - 2 || i === currentPage + 2) {
             html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }

    html += `<li class="page-item ${currentPage === totalPages || totalPages === 0 ? 'disabled' : ''}">
                <a class="page-link cursor-pointer" onclick="goToPage(${currentPage + 1})"><i class="bi bi-chevron-right"></i></a>
             </li>`;

    navEl.innerHTML = html;
}

function goToPage(page) {
    if (page < 1) return;
    currentPage = page;
    renderLogHistory(filteredLogsGlobal); 
}

function changeRowsPerPage(rows) {
    rowsPerPage = parseInt(rows);
    currentPage = 1; 
    renderLogHistory(filteredLogsGlobal);
}

function getLocalYMD(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}

// ==========================================
// 7. EXPORT / IMPORT CSV (QUARTERLY SUPPORTED)
// ==========================================

function exportReport(mode) {
    const modeNames = { 'daily': 'รายวัน', 'monthly': 'รายเดือน', 'quarterly': 'รายไตรมาส', 'yearly': 'รายปี' };
    if (!confirm(`ยืนยันการดาวน์โหลดรายงาน "${modeNames[mode]}" หรือไม่?`)) return;

    const today = new Date();
    let startDate, endDate;

    switch(mode) {
        case 'daily': 
            startDate = new Date(today); 
            endDate = new Date(today); 
            break;
        case 'monthly': 
            startDate = new Date(today.getFullYear(), today.getMonth(), 1); 
            endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0); 
            break;
        case 'quarterly': 
            // 🌟 คำนวณไตรมาสตามเวลาปัจจุบัน (ปีงบประมาณไทย: ต.ค. คือเริ่ม Q1)
            const currentMonth = today.getMonth(); // 0-11
            let qYear = today.getFullYear();
            let startMonth, endMonth;

            if (currentMonth >= 9) { // ต.ค. - ธ.ค. (Q1 ปีงบใหม่)
                startMonth = 9; endMonth = 11;
            } else if (currentMonth >= 0 && currentMonth <= 2) { // ม.ค. - มี.ค. (Q2)
                startMonth = 0; endMonth = 2;
            } else if (currentMonth >= 3 && currentMonth <= 5) { // เม.ย. - มิ.ย. (Q3)
                startMonth = 3; endMonth = 5;
            } else { // ก.ค. - ก.ย. (Q4)
                startMonth = 6; endMonth = 8;
            }
            startDate = new Date(qYear, startMonth, 1);
            endDate = new Date(qYear, endMonth + 1, 0);
            break;
        case 'yearly': 
            startDate = new Date(today.getFullYear(), 0, 1); 
            endDate = new Date(today.getFullYear(), 11, 31); 
            break;
        default: return;
    }
    
    let currentPath = window.location.pathname;
    let exportPath = currentPath.replace(/\/report\/?$/, '/report/export/');
    
    let selectedDepts = [];
    const userTypeElement = document.querySelector('input[name="userTypeOption"]:checked');
    const userType = userTypeElement ? userTypeElement.value : 'all';
    
    if (userType === 'student') {
        document.querySelectorAll('#studentFacultyList input[type="checkbox"]:checked').forEach(cb => {
            selectedDepts.push(cb.value);
        });
    } else if (userType === 'staff') {
        document.querySelectorAll('#staffOrgList input[type="checkbox"]:checked').forEach(cb => {
            selectedDepts.push(cb.value);
        });
    }

    let deptQuery = "";
    if (selectedDepts.length > 0) {
        deptQuery = `&department=${encodeURIComponent(selectedDepts.join(','))}`;
    }
    
    window.location.href = `${exportPath}?start_date=${getLocalYMD(startDate)}&end_date=${getLocalYMD(endDate)}${deptQuery}`;
}

function downloadReportCSVTemplate() {
    const headers = ["รหัสผู้ใช้", "ชื่อ-สกุล", "Software", "วันที่", "เวลา (เข้า-ออก)", "คณะ/หน่วยงาน", "ชั้นปี", "ประเภท", "PC"];
    const sampleRows = [
        ["68114540353", "นายปภังกร นิชรัตน์", "ChatGPT", "04/03/2026", "09:00 - 10:30", "คณะวิทยาศาสตร์", "ปี 1", "นักศึกษา", "PC-01"],
        ["scwayopu", "อ.วาโย ปุยะติ", "Canva", "04/03/2026", "13:00 - 15:00", "คณะวิทยาศาสตร์", "-", "บุคลากร", "PC-05"],
        ["guest999", "บุคคลภายนอก", "ChatGPT", "04/03/2026", "10:00 - 11:00", "บุคคลภายนอก", "-", "บุคคลภายนอก", "PC-02"]
    ];

    let csvContent = headers.join(",") + "\n";
    sampleRows.forEach(row => {
        const safeRow = row.map(cell => (cell && String(cell).includes(',')) ? `"${cell}"` : cell);
        csvContent += safeRow.join(",") + "\n";
    });

    const bom = new Uint8Array([0xEF, 0xBB, 0xBF]);
    const blob = new Blob([bom, csvContent], { type: 'text/csv;charset=utf-8;' });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "CKLab_Log_Template.csv"); 
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}