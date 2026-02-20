"""
python manage.py seed_data
สร้างข้อมูลเริ่มต้น: Software, Computer, UsageLog (50 records), Booking (15 records), SiteConfig, AdminonDuty, superuser
"""
import random
from datetime import timedelta, date, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from lab_management.models import Software, Computer, UsageLog, Booking, SiteConfig, AdminonDuty


# ── ข้อมูลตัวอย่าง ──────────────────────────────────────────────────────────

STUDENTS = [
    ("65010001", "สมชาย ใจดี",       "student", "วิทยาศาสตร์", "3"),
    ("65010002", "สมหญิง รักเรียน",  "student", "วิทยาศาสตร์", "2"),
    ("65010003", "ธนา มั่งมี",        "student", "วิศวกรรมศาสตร์", "4"),
    ("65010004", "นภา สดใส",          "student", "วิศวกรรมศาสตร์", "1"),
    ("65010005", "กิตติ เก่งกาจ",    "student", "เทคโนโลยีสารสนเทศ", "3"),
    ("65010006", "พิมพ์ สวยงาม",      "student", "เทคโนโลยีสารสนเทศ", "2"),
    ("65010007", "อนุชา ขยันหมั่น",  "student", "บริหารธุรกิจ", "1"),
    ("65010008", "มนัส ตั้งใจ",       "student", "บริหารธุรกิจ", "4"),
    ("65010009", "รัตนา ฉลาด",        "student", "วิทยาศาสตร์", "2"),
    ("65010010", "ชนะ วิริยะ",        "student", "วิศวกรรมศาสตร์", "3"),
    ("65010011", "ดวงใจ สุขสันต์",   "student", "เทคโนโลยีสารสนเทศ", "1"),
    ("65010012", "ปรีชา เฉลียวฉลาด", "student", "วิทยาศาสตร์", "4"),
    ("ST001",    "อาจารย์ สมศักดิ์ ดีงาม",  "staff",   "คณะวิทยาศาสตร์",  None),
    ("ST002",    "อาจารย์ วิไล มีคุณ",       "staff",   "คณะวิศวกรรมศาสตร์", None),
    ("ST003",    "นาย สมบัติ บริการ",        "staff",   "สำนักงานกลาง",     None),
    ("EX001",    "นาย John Smith",            "guest",   "มหาวิทยาลัยเชียงใหม่", None),
    ("EX002",    "นาง Maria Garcia",          "guest",   "บริษัท TechCorp",  None),
    ("EX003",    "นาย ทรงวุฒิ ภายนอก",      "guest",   "กรมวิทยาศาสตร์",   None),
]

COMMENTS_GOOD = [
    "ระบบดีมาก ใช้งานง่าย",
    "AI ช่วยงานได้มากเลย",
    "ห้องสะอาด บรรยากาศดี",
    "เครื่องเร็วดี ทำงานได้สะดวก",
    "ชอบมาก จะกลับมาใช้อีก",
    "Claude ช่วยเขียนโค้ดได้ดีมาก",
    "Gemini ตอบคำถามได้ดีเลย",
]
COMMENTS_MID = [
    "โอเค ใช้ได้ปกติ",
    "ดีพอสมควร",
    "",
    "",
    "",
]
COMMENTS_BAD = [
    "อินเทอร์เน็ตช้านิดหน่อย",
    "เก้าอี้นั่งนานแล้วปวดหลัง",
    "",
]

SOFTWARE_LIST = [
    ("ChatGPT", "Plus",    "AI"),
    ("Gemini",  "Pro",     "AI"),
    ("Claude",  "Pro",     "AI"),
    ("Canva",   "Pro",     "Software"),
]

# กระจาย software ให้ PC: chatgpt 3, gemini 3, claude 3, canva 1 = 10 เครื่อง
PC_SOFTWARE_MAP = {
    "PC-01": "ChatGPT", "PC-02": "ChatGPT", "PC-03": "ChatGPT",
    "PC-04": "Gemini",  "PC-05": "Gemini",  "PC-06": "Gemini",
    "PC-07": "Claude",  "PC-08": "Claude",  "PC-09": "Claude",
    "PC-10": "Canva",
}


class Command(BaseCommand):
    help = "Seed initial data: software, computers, 50 usage logs, site config, superuser"

    def handle(self, *args, **options):
        self.stdout.write("=== Seeding data ===\n")

        self._create_software()
        self._create_computers()
        self._create_site_config()
        self._create_usage_logs()
        self._create_bookings()
        self._create_superuser()

        self.stdout.write(self.style.SUCCESS("\n=== Done! ==="))

    # ── Software ─────────────────────────────────────────────────────────────

    def _create_software(self):
        for name, version, sw_type in SOFTWARE_LIST:
            obj, created = Software.objects.get_or_create(
                name=name,
                defaults={
                    "version": version,
                    "type": sw_type,
                    "expire_date": date(2026, 12, 31),
                },
            )
            status = "created" if created else "exists"
            self.stdout.write(f"  Software [{status}]: {obj}")

    # ── Computers ────────────────────────────────────────────────────────────

    def _create_computers(self):
        for pc_name, sw_name in PC_SOFTWARE_MAP.items():
            software = Software.objects.get(name=sw_name)
            obj, created = Computer.objects.get_or_create(
                name=pc_name,
                defaults={"Software": software, "status": "AVAILABLE"},
            )
            status = "created" if created else "exists"
            self.stdout.write(f"  Computer [{status}]: {obj.name} → {sw_name}")

    # ── SiteConfig + AdminonDuty ─────────────────────────────────────────────

    def _create_site_config(self):
        duty, _ = AdminonDuty.objects.get_or_create(
            admin_on_duty="ผศ.ดร. สมศรี ดูแลดี",
            defaults={
                "contact_phone": "081-234-5678",
                "contact_email": "admin@cklab.ubu.ac.th",
            },
        )
        config, created = SiteConfig.objects.get_or_create(
            id=1,
            defaults={
                "lab_name": "CKLab",
                "location": "อาคาร 4 ชั้น 2 มหาวิทยาลัยอุบลราชธานี",
                "booking_enabled": True,
                "is_open": True,
                "admin_on_duty": duty,
                "announcement": "ยินดีต้อนรับสู่ CKLab — กรุณาเช็คอินก่อนใช้งาน",
            },
        )
        status = "created" if created else "exists"
        self.stdout.write(f"  SiteConfig [{status}]: {config.lab_name}")

    # ── UsageLog (50 records) ─────────────────────────────────────────────────

    def _create_usage_logs(self):
        """
        สร้าง UsageLog 50 รายการ กระจาย 30 วันย้อนหลัง
        - distribution: student ~65%, staff ~20%, guest ~15%
        - software: chatgpt ~35%, gemini ~30%, claude ~25%, canva ~10%
        - score: 5★ ~40%, 4★ ~35%, 3★ ~15%, 2★ ~7%, 1★ ~3%  → กราฟ right-skewed สวย
        - เวลาใช้: 30–180 นาที กระจาย peak ช่วงเช้า (09-12) และบ่าย (13-16)
        """
        if UsageLog.objects.count() >= 50:
            self.stdout.write("  UsageLog: already seeded, skip")
            return

        now = timezone.now()
        computers = list(Computer.objects.all())

        # weights สำหรับ software ใน log
        sw_weights = {
            "ChatGPT": 35, "Gemini": 30, "Claude": 25, "Canva": 10
        }
        sw_pool = []
        for sw, w in sw_weights.items():
            sw_pool.extend([sw] * w)

        # score distribution
        score_pool = [5]*40 + [4]*35 + [3]*15 + [2]*7 + [1]*3

        # user type distribution
        student_users = [u for u in STUDENTS if u[2] == "student"]
        staff_users   = [u for u in STUDENTS if u[2] == "staff"]
        guest_users   = [u for u in STUDENTS if u[2] == "guest"]
        user_pool = (student_users * 7) + (staff_users * 4) + (guest_users * 3)

        peak_hours = [9, 9, 10, 10, 11, 13, 13, 14, 14, 15, 16]

        created_count = 0
        for i in range(50):
            user = random.choice(user_pool)
            uid, uname, utype, dept, year = user

            # กระจายวันใน 30 วันย้อนหลัง — หนักช่วง 2 สัปดาห์หลัง
            days_ago = random.choices(
                population=list(range(1, 31)),
                weights=[max(1, 31 - d) for d in range(1, 31)],
            )[0]
            hour  = random.choice(peak_hours)
            minute = random.choice([0, 15, 30, 45])
            duration = random.randint(30, 180)  # นาที

            start_dt = now - timedelta(days=days_ago, hours=now.hour - hour, minutes=now.minute - minute)
            # ปรับให้ตรงชั่วโมงที่กำหนด
            start_dt = start_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
            end_dt   = start_dt + timedelta(minutes=duration)

            software_name = random.choice(sw_pool)
            pc = random.choice(computers)
            score = random.choice(score_pool)

            if score >= 4:
                comment = random.choice(COMMENTS_GOOD)
            elif score == 3:
                comment = random.choice(COMMENTS_MID)
            else:
                comment = random.choice(COMMENTS_BAD)

            log = UsageLog(
                user_id=uid,
                user_name=uname,
                user_type=utype,
                department=dept,
                user_year=year,
                computer=pc.name,
                Software=software_name,
                end_time=end_dt,
                satisfaction_score=score,
                comment=comment,
            )
            # บายพาส auto_now_add โดย save แล้วอัพเดต start_time ผ่าน queryset
            log.save()
            UsageLog.objects.filter(pk=log.pk).update(start_time=start_dt)
            created_count += 1

        self.stdout.write(f"  UsageLog: created {created_count} records")

    # ── Booking (15 records) ─────────────────────────────────────────────────

    def _create_bookings(self):
        """
        สร้าง Booking 15 รายการ กระจายใน 7 วันข้างหน้า (อนาคต)
        - ทุก record เป็น APPROVED แล้ว (ไม่มี PENDING/REJECTED ตาม req)
        - กระจายให้ครอบ time slot หลากหลาย
        - Computer ที่มี Booking จะตั้ง status = RESERVED
        """
        if Booking.objects.count() >= 15:
            self.stdout.write("  Booking: already seeded, skip")
            return

        # time slots ตาม design
        TIME_SLOTS = [
            (time(9, 0),  time(10, 30)),
            (time(10, 30), time(12, 0)),
            (time(13, 30), time(15, 0)),
            (time(15, 0),  time(16, 30)),
        ]

        now   = timezone.now()
        today = now.date()

        computers = list(Computer.objects.all())
        student_ids = [u[0] for u in STUDENTS if u[2] == "student"]

        # กระจาย booking ใน 7 วันข้างหน้า วันละ 2-3 รายการ
        booking_plan = [
            # (days_from_today, pc_index, slot_index, student_id)
            (1, 0, 0, student_ids[0]),
            (1, 3, 1, student_ids[1]),
            (1, 6, 2, student_ids[2]),
            (2, 1, 0, student_ids[3]),
            (2, 4, 3, student_ids[4]),
            (3, 2, 1, student_ids[5]),
            (3, 7, 2, student_ids[6]),
            (3, 9, 0, student_ids[7]),
            (4, 0, 3, student_ids[8]),
            (4, 5, 1, student_ids[9]),
            (5, 3, 0, student_ids[10]),
            (5, 8, 2, student_ids[11]),
            (6, 1, 1, student_ids[0]),
            (6, 6, 3, student_ids[2]),
            (7, 4, 0, student_ids[4]),
        ]

        reserved_pcs = set()
        created_count = 0

        for days_ahead, pc_idx, slot_idx, student_id in booking_plan:
            pc   = computers[pc_idx % len(computers)]
            slot = TIME_SLOTS[slot_idx]
            booking_date = today + timedelta(days=days_ahead)

            import datetime as dt
            start_dt = timezone.make_aware(dt.datetime.combine(booking_date, slot[0]))
            end_dt   = timezone.make_aware(dt.datetime.combine(booking_date, slot[1]))

            Booking.objects.create(
                student_id=student_id,
                computer=pc,
                start_time=start_dt,
                end_time=end_dt,
                booking_date=now,
                status="APPROVED",
            )

            # PC ที่จองวันนี้หรือพรุ่งนี้ → RESERVED
            if days_ahead <= 2 and pc.pk not in reserved_pcs:
                Computer.objects.filter(pk=pc.pk).update(status="RESERVED")
                reserved_pcs.add(pc.pk)

            created_count += 1

        self.stdout.write(f"  Booking: created {created_count} records ({len(reserved_pcs)} PCs → RESERVED)")

    # ── Superuser ─────────────────────────────────────────────────────────────

    def _create_superuser(self):
        username = "admin"
        password = "admin1234"
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  Superuser [{username}]: already exists")
            return
        User.objects.create_superuser(
            username=username,
            password=password,
            email="admin@cklab.ubu.ac.th",
            first_name="Super",
            last_name="Admin",
        )
        self.stdout.write(
            self.style.SUCCESS(f"  Superuser created → username: {username}  password: {password}")
        )
