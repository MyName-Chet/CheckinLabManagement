# ระบบ… Topics

\`

 

โครงงานนี้เป็นส่วนหนึ่งของการศึกษา

หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาวิทยาการข้อมูลและนวัตกรรมซอฟต์แวร์

ภาควิชาคณิตศาสตร์ สถิติ และคอมพิวเตอร์ คณะวิทยาศาสตร์

มหาวิทยาลัยอุบลราชธานี

ปีการศึกษา 25..

**ลิขสิทธิ์ของมหาวิทยาลัยอุบลราชธานี**

# สมาชิกกลุ่ม 


   

   # กิตติกรรมประกาศ

   # 

   # สารบัญ

# 

# บทที่ 1 บทนำ

## **1.1 ความเป็นมาและความสำคัญของปัญหา**

ปัญหาของระบบ …

ความจำเป็นของระบบดิจิทัลในการบริหารจัดการ …

ที่มาของโครงงาน ..

## **1.2 วัตถุประสงค์ของโครงงาน**

## **1.3 ขอบเขตของโครงงาน**

### 1.3.1 ฟังก์ชันที่พัฒนา

### 1.3.2 กลุ่มผู้ใช้งาน (นักศึกษา, บุคลากร, ผู้ดูแลระบบ)

### 1.3.3 ขอบเขตที่ไม่รวม (ถ้ามี)

## **1.4 ประโยชน์ที่คาดว่าจะได้รับ**

1\. 

2\. 

## **1.5 นิยามศัพท์ / คำจำกัดความ (ถ้ามี)** 

## 

## **1.6 แผนการดำเนินงาน** 

อาจเขียนรูปแบบ ตาราง หรือ Gantt chart  

ตัวอย่างแบบตาราง

| ลำดับ | งานที่ต้องทำ | กำหนดเวลาส่งงาน |
| :---- | :---- | :---- |
| 1 | รับความต้องการของระบบ | ธันวาคม 68 |
|  |  |  |

# 

# บทที่ 2  การวิเคราะห์ความต้องการ

## **2.1 การเก็บรวบรวมความต้องการ**

### 2.1.1 วิธีการเก็บข้อมูล (สัมภาษณ์, สังเกตการณ์, แบบสอบถาม)

### 2.1.2 ผู้มีส่วนได้ส่วนเสีย (Stakeholders)

## **2.2 ความต้องการเชิงหน้าที่ (Functional Requirements)**


## **2.3 Use Case Diagram**

ภาพ พร้อมคำอธิบาย เป็นตาราง รวม

## **2.4 คำอธิบาย Use Case (Use Case Description)**

คำอธิบายราย Use case

# 

# บทที่ 3  การออกแบบระบบ

## **3.1 สถาปัตยกรรมระบบ (System Architecture)**

 ภาพรวมสถาปัตยกรรม (MVT Pattern)

คำอธิบายส่วนประกอบของระบบ

## **3.2 ข้อมูลที่เกี่ยวข้องกับระบบ**

ขอ้มูลที่ได้จากการเก็บความต้องการ

## **3.3 การออกแบบ URL / API Endpoints**

### 3.3.1 URL Pattern app 1

### 3.3.2 URL Pattern app2

## **3.4 การออกแบบส่วนติดต่อผู้ใช้ (UI/UX Design)**

ภาพพร้อมคำอธิบาย ที่นำเสนอตอนกลางภาค

## **3.5 Activity Diagram**

ภาพพร้อมคำอธิบาย ที่นำเสนอตอนกลางภาค

# 

# บทที่ 4  การพัฒนาระบบ

## **4.1 เครื่องมือและเทคโนโลยีที่ใช้**

ตัวอย่าง

- Backend: Python 3.10+, Django 5.0  
- Database: PostgreSQL 15 (Docker)  
- Frontend: Bootstrap 5.3, Vanilla JavaScript  
- เครื่องมือเสริม: uv, Docker Compose, Git

## **4.2 การพัฒนา Models (Database Layer)**

อธิบายส่วน Models พร้อมคำอธิบาย Data dictionary

## **4.3 การพัฒนา Views (Business Logic Layer)**

อธิบายส่วน views/ controller 

## **4.4 การพัฒนา Frontend**

อธิบายส่วน .html 

## **4.5 การแบ่งงานของสมาชิกในทีม**

ตัวอย่าง (ที่ส่งสัปดาห์ก่อนหน้านี้)

| สมาชิก | ความรับผิดชอบ | Business logic ที่รับผิดชอบ |
| :---- | :---- | :---- |
| ปภังกร | Kiosk UI, Check-in/out, Feedback | IndexView, CheckinView, CheckoutView, FeedbackView |
| สถาพร | Authentication, Login/Logout | LoginView, LogoutView |
| ภานุวัฒน์ | Config & User Management | AdminConfigView, AdminUserView, AdminUserEditView, AdminUserDeleteView |
| ธนสิทธิ์ | Monitor Dashboard, Real-time API | AdminMonitorView, AdminMonitorDataAPIView, AdminCheckinView, AdminCheckoutView |
| อัษฎาวุธ | Booking System, CSV Import | AdminBookingView, AdminImportBookingView, AdminBookingDetailView |
| ณัฐกรณ์ | PC Management | AdminManagePcView, AdminAddPcView, AdminManagePcEditView, AdminManagePcDeleteView |
| ลลิดา | Software Management | AdminSoftwareView, AdminSoftwareEditView, AdminSoftwareDeleteView |
| เขมมิกา | Reporting, CSV Export | AdminReportView, AdminReportExportView |

# 

# บทที่ 5  การทดสอบระบบ (Testing)

## **5.1 การทดสอบหน่วย (Unit Testing)**

การทดสอบราย Business logic

## **5.2 การทดสอบระบบ (System Testing)**

Test Case ฟังก์ชันหลักทุกข้อ

## **5.3 สรุปผลการทดสอบและปัญหาที่พบ**

# 

# บทที่ 6  สรุปผลและงานต่อยอด

## **6.1 สรุปผลการดำเนินงาน**

### 6.1.1 สิ่งที่พัฒนาสำเร็จ

### 6.1.2 เปรียบเทียบผลลัพธ์กับวัตถุประสงค์

## **6.2 ปัญหาและอุปสรรคที่พบ**

### 6.2.1 หัวข้อ(ตัวอย่าง) ผู้พัฒนาไม่เข้าใจศัพท์เทคนิคของลูกค้า 

1. #### ปัญหาที่พบ

2. #### วิธีแก้ไข 

3. #### ผลของการแก้ปัญหา (ถ้ามี)

## **6.3 สิ่งที่ได้เรียนรู้ (Lessons Learned)**

### 6.3.1 ด้านเทคโนโลยี (Django, PostgreSQL, Docker)

### 6.3.2 ด้านการทำงานเป็นทีม (Git Workflow)

### 6.3.3 ด้านความเข้าใจในระบบธุรกิจ (ถ้ามี)

## **6.4 ข้อเสนอแนะและงานต่อยอด (Future Work)**

(ตัวอย่าง)

- ระบบแจ้งเตือนผ่าน LINE Notify / Email ในฟังก์ชัน ..  เพื่อเสริมใน …  เพราะว่า   
- รองรับ Fingerprint หรือ RFID สำหรับ Check-in  
- Mobile App สำหรับนักศึกษา  
- ระบบ AI วิเคราะห์รูปแบบการใช้งาน  
- รองรับหลายห้อง Lab

## **6.5 บทสรุป (Conclusion)**

# 

# บรรณานุกรม

ให้ใช้มาตรฐานการเขียนอ้างอิง**รูปแบบ Chicago**

ตัวอย่าง

\[1\] Django REST framework. "Django REST framework." Accessed February 26, 2025\. [https://www.django-rest-framework.org/](https://www.django-rest-framework.org/).

# 

# ภาคผนวก ก. การติดตั้งระบบ

### ก.1 ความต้องการของระบบ (System Requirements)

- Python 3.10+  
- Docker & Docker Compose  
- Git

### ก.2 การติดตั้งสภาพแวดล้อม

- สร้าง Virtual Environment (`uv venv`)  
- ติดตั้ง Dependencies (`uv pip install -r requirements.txt`)

### ก.3 การตั้งค่าฐานข้อมูล

- รัน Docker Compose (`docker compose up -d`)  
- สร้างตาราง (`python manage.py migrate`)  
- โหลดข้อมูลตัวอย่าง (`python manage.py seed_data`)

### ก.4 การตั้งค่าไฟล์ `.env`

- ตัวแปรสภาพแวดล้อมที่จำเป็น (SECRET\_KEY, DB credentials)

### ก.5 การรันระบบ

- `python manage.py runserver`  
- URL สำหรับเข้าถึงระบบ

### ก.6 การ Deploy บนเซิร์ฟเวอร์จริง

- ตั้งค่า DEBUG=False  
- Static Files  
- การตั้งค่า ALLOWED\_HOSTS

# ภาคผนวก ข. คู่มือการใช้งาน

### ข.1 คู่มือสำหรับผู้ใช้ทั่วไป (Kiosk)

- การ Check-in เข้าใช้งาน  
- การดูสถานะเซสชัน (Timer)  
- การ Check-out ออกจากระบบ  
- การให้ Feedback หลังใช้งาน

### ข.2 คู่มือสำหรับผู้ดูแลระบบ (Admin)

- การเข้าสู่ระบบ Admin Portal  
- การใช้งาน Monitor Dashboard  
  - การดูสถานะคอมพิวเตอร์แบบ Real-time  
  - การ Check-in / Check-out แทนผู้ใช้  
- การจัดการ Booking  
  - การสร้าง Booking  
  - การ Import CSV  
- การจัดการคอมพิวเตอร์ (เพิ่ม/แก้ไข/ลบ)  
- การจัดการซอฟต์แวร์  
- การดูรายงานและ Export CSV  
- การจัดการบัญชีผู้ดูแล  
- การตั้งค่าระบบ
