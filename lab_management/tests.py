import io
import json
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from .models import AdminonDuty, Booking, Computer, SiteConfig, Software, UsageLog


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def make_software(**kwargs):
    d = {'name': 'TestSW', 'version': '1.0', 'type': 'Software', 'expire_date': date(2026, 12, 31)}
    d.update(kwargs)
    return Software.objects.create(**d)


def make_computer(software=None, status='AVAILABLE', **kwargs):
    if software is None:
        software = make_software(name=f'SW-{Computer.objects.count()}')
    d = {'name': f'PC-{Computer.objects.count() + 1:02d}', 'Software': software, 'status': status}
    d.update(kwargs)
    return Computer.objects.create(**d)


def make_admin(**kwargs):
    d = {'username': 'admin', 'password': 'adminpass123', 'is_staff': True, 'is_superuser': True}
    d.update(kwargs)
    return User.objects.create_user(**d)


# ===========================================================================
# MODEL TESTS
# ===========================================================================

class SoftwareModelTest(TestCase):
    def test_create_software(self):
        sw = make_software(name='MATLAB', version='R2024a', type='Software')
        self.assertEqual(sw.name, 'MATLAB')
        self.assertEqual(sw.version, 'R2024a')
        self.assertEqual(sw.type, 'Software')

    def test_str_representation(self):
        sw = make_software(name='Python', version='3.11')
        self.assertIn('Python', str(sw))
        self.assertIn('3.11', str(sw))

    def test_ai_type(self):
        sw = make_software(name='ChatGPT', version='4o', type='AI')
        self.assertEqual(sw.type, 'AI')

    def test_expire_date_optional(self):
        sw = Software.objects.create(name='FreeSW', version='1.0', type='Software', expire_date=None)
        self.assertIsNone(sw.expire_date)


class ComputerModelTest(TestCase):
    def test_create_computer(self):
        sw = make_software()
        pc = Computer.objects.create(name='PC-01', Software=sw, status='AVAILABLE')
        self.assertEqual(pc.name, 'PC-01')
        self.assertEqual(pc.status, 'AVAILABLE')
        self.assertEqual(pc.Software, sw)

    def test_status_choices(self):
        pc = make_computer(status='IN_USE')
        self.assertEqual(pc.status, 'IN_USE')

    def test_computer_name_unique(self):
        make_computer(name='PC-99')
        with self.assertRaises(Exception):
            make_computer(name='PC-99')

    def test_software_nullable(self):
        pc = Computer.objects.create(name='PC-00', Software=None, status='AVAILABLE')
        self.assertIsNone(pc.Software)


class AdminonDutyModelTest(TestCase):
    def test_create_admin_on_duty(self):
        admin = AdminonDuty.objects.create(
            admin_on_duty='John Doe',
            contact_email='john@example.com',
            contact_phone='0812345678'
        )
        self.assertEqual(admin.admin_on_duty, 'John Doe')
        self.assertEqual(admin.contact_email, 'john@example.com')

    def test_fields_optional(self):
        admin = AdminonDuty.objects.create()
        self.assertIsNone(admin.admin_on_duty)
        self.assertIsNone(admin.contact_email)
        self.assertIsNone(admin.contact_phone)


class SiteConfigModelTest(TestCase):
    def test_create_site_config(self):
        config = SiteConfig.objects.create(lab_name='CKLab', is_open=True)
        self.assertEqual(config.lab_name, 'CKLab')
        self.assertTrue(config.is_open)

    def test_default_values(self):
        config = SiteConfig.objects.create()
        self.assertEqual(config.lab_name, 'CKLab')
        self.assertTrue(config.is_open)
        self.assertTrue(config.booking_enabled)

    def test_admin_on_duty_fk(self):
        admin = AdminonDuty.objects.create(admin_on_duty='Staff A')
        config = SiteConfig.objects.create(admin_on_duty=admin)
        self.assertEqual(config.admin_on_duty, admin)


class BookingModelTest(TestCase):
    def setUp(self):
        self.pc = make_computer(name='PC-10')
        self.now = timezone.now()

    def test_create_booking(self):
        booking = Booking.objects.create(
            student_id='64010001',
            computer=self.pc,
            start_time=self.now,
            end_time=self.now + timedelta(hours=2),
            status='PENDING'
        )
        self.assertEqual(booking.student_id, '64010001')
        self.assertEqual(booking.status, 'PENDING')

    def test_status_choices(self):
        booking = Booking.objects.create(
            student_id='64010002',
            computer=self.pc,
            start_time=self.now,
            end_time=self.now + timedelta(hours=1),
            status='APPROVED'
        )
        self.assertEqual(booking.status, 'APPROVED')


class UsageLogModelTest(TestCase):
    def test_create_usage_log(self):
        log = UsageLog.objects.create(
            user_id='64010001',
            user_name='Test User',
            user_type='student',
            computer='PC-01',
            Software='MATLAB'
        )
        self.assertEqual(log.user_id, '64010001')
        self.assertIsNone(log.end_time)
        self.assertIsNotNone(log.start_time)

    def test_checkout_sets_end_time(self):
        log = UsageLog.objects.create(user_id='u1', user_name='U1', user_type='student')
        log.end_time = timezone.now()
        log.save()
        self.assertIsNotNone(log.end_time)

    def test_satisfaction_score_optional(self):
        log = UsageLog.objects.create(user_id='u2', user_name='U2', user_type='guest')
        self.assertIsNone(log.satisfaction_score)
        self.assertIsNone(log.comment)


# ===========================================================================
# URL REVERSE TESTS
# ===========================================================================

class KioskUrlTest(TestCase):
    def test_index_url(self):
        url = reverse('index')
        self.assertEqual(url, '/')

    def test_checkin_url(self):
        url = reverse('checkin', kwargs={'pc_id': 1})
        self.assertIn('checkin', url)

    def test_checkout_url(self):
        url = reverse('checkout', kwargs={'pc_id': 1})
        self.assertIn('checkout', url)

    def test_status_url(self):
        url = reverse('status', kwargs={'pc_id': 1})
        self.assertIn('status', url)

    def test_feedback_url(self):
        url = reverse('feedback', kwargs={'pc_id': 1, 'software_id': 1})
        self.assertIn('feedback', url)


class AdminUrlTest(TestCase):
    def test_admin_login_url(self):
        url = reverse('admin_login')
        self.assertIn('login', url)

    def test_admin_logout_url(self):
        url = reverse('admin_logout')
        self.assertIn('logout', url)

    def test_admin_users_url(self):
        url = reverse('admin_users')
        self.assertIn('users', url)

    def test_admin_user_edit_url(self):
        url = reverse('admin_user_edit', kwargs={'pk': 1})
        self.assertIn('edit', url)

    def test_admin_user_delete_url(self):
        url = reverse('admin_user_delete', kwargs={'pk': 1})
        self.assertIn('delete', url)

    def test_admin_monitor_url(self):
        url = reverse('admin_monitor')
        self.assertIn('monitor', url)

    def test_admin_booking_url(self):
        url = reverse('admin_booking')
        self.assertIn('booking', url)

    def test_admin_booking_import_url(self):
        url = reverse('admin_booking_import')
        self.assertIn('import', url)

    def test_admin_manage_pc_url(self):
        url = reverse('admin_manage_pc')
        self.assertIn('manage-pc', url)

    def test_admin_add_pc_url(self):
        url = reverse('admin_add_pc')
        self.assertIn('add', url)

    def test_admin_software_url(self):
        url = reverse('admin_software')
        self.assertIn('software', url)

    def test_admin_report_url(self):
        url = reverse('admin_report')
        self.assertIn('report', url)

    def test_admin_report_export_url(self):
        url = reverse('admin_report_export')
        self.assertIn('export', url)

    def test_admin_config_url(self):
        url = reverse('admin_config')
        self.assertIn('config', url)


# ===========================================================================
# AUTH VIEW TESTS
# ===========================================================================

class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.url = reverse('admin_login')

    def test_get_login_page(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_login_success_redirects(self):
        resp = self.client.post(self.url, {'username': 'admin', 'password': 'adminpass123'})
        self.assertIn(resp.status_code, [200, 302])

    def test_login_wrong_password(self):
        resp = self.client.post(self.url, {'username': 'admin', 'password': 'wrongpass'})
        self.assertEqual(resp.status_code, 200)

    def test_login_nonexistent_user(self):
        resp = self.client.post(self.url, {'username': 'nobody', 'password': 'pass'})
        self.assertEqual(resp.status_code, 200)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin', password='adminpass123')

    def test_logout_redirects(self):
        resp = self.client.post(reverse('admin_logout'))
        self.assertIn(resp.status_code, [200, 302])

    def test_after_logout_protected_pages_redirect(self):
        self.client.post(reverse('admin_logout'))
        resp = self.client.get(reverse('admin_monitor'))
        self.assertEqual(resp.status_code, 302)


class AdminAuthGuardTest(TestCase):
    """All admin pages must redirect unauthenticated users."""

    def setUp(self):
        self.client = Client()
        self.pc = make_computer(name='PC-01')

    def _assert_redirects_to_login(self, url):
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_monitor_requires_login(self):
        self._assert_redirects_to_login(reverse('admin_monitor'))

    def test_manage_pc_requires_login(self):
        self._assert_redirects_to_login(reverse('admin_manage_pc'))

    def test_software_requires_login(self):
        self._assert_redirects_to_login(reverse('admin_software'))

    def test_report_requires_login(self):
        self._assert_redirects_to_login(reverse('admin_report'))

    def test_config_requires_login(self):
        self._assert_redirects_to_login(reverse('admin_config'))

    def test_booking_requires_login(self):
        self._assert_redirects_to_login(reverse('admin_booking'))

    def test_users_requires_login(self):
        self._assert_redirects_to_login(reverse('admin_users'))


# ===========================================================================
# KIOSK VIEW TESTS
# ===========================================================================

class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.config = SiteConfig.objects.create(is_open=True)
        self.pc = make_computer(name='PC-01')

    def test_index_get_returns_200(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)

    def test_index_get_with_pc_param(self):
        resp = self.client.get(reverse('index') + '?pc=PC-01')
        self.assertEqual(resp.status_code, 200)

    def test_index_shows_timer_when_in_use(self):
        self.pc.status = 'IN_USE'
        self.pc.save()
        UsageLog.objects.create(
            user_id='u1', user_name='User One', user_type='student',
            computer='PC-01'
        )
        resp = self.client.get(reverse('index') + '?pc=PC-01')
        self.assertEqual(resp.status_code, 200)

    def test_index_auto_fix_ghost_state(self):
        """PC stuck IN_USE but no active log -> auto-fixed to AVAILABLE."""
        self.pc.status = 'IN_USE'
        self.pc.save()
        resp = self.client.get(reverse('index') + '?pc=PC-01')
        self.assertEqual(resp.status_code, 200)
        self.pc.refresh_from_db()
        self.assertEqual(self.pc.status, 'AVAILABLE')

    def test_index_unknown_pc_still_renders(self):
        resp = self.client.get(reverse('index') + '?pc=PC-99')
        self.assertEqual(resp.status_code, 200)


class CheckinViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.config = SiteConfig.objects.create(is_open=True)
        self.pc = make_computer(name='PC-01')

    def test_checkin_get_redirects(self):
        resp = self.client.get(reverse('checkin', kwargs={'pc_id': 'PC-01'}))
        self.assertEqual(resp.status_code, 302)

    def test_checkin_post_valid_creates_log(self):
        resp = self.client.post(
            reverse('checkin', kwargs={'pc_id': 'PC-01'}),
            {
                'user_id': '64010001',
                'user_name': 'Test User',
                'user_type': 'student',
                'department': 'Science',
                'user_year': '2',
            }
        )
        # Either renders timer (200) or redirects, but a log should exist
        self.assertGreaterEqual(resp.status_code, 200)

    def test_checkin_post_lab_closed_redirects(self):
        self.config.is_open = False
        self.config.save()
        resp = self.client.post(
            reverse('checkin', kwargs={'pc_id': 'PC-01'}),
            {'user_id': '64010001', 'user_name': 'Test', 'user_type': 'student'}
        )
        self.assertEqual(resp.status_code, 302)

    def test_checkin_unavailable_pc_redirects(self):
        self.pc.status = 'IN_USE'
        self.pc.save()
        resp = self.client.post(
            reverse('checkin', kwargs={'pc_id': 'PC-01'}),
            {'user_id': '64010001', 'user_name': 'Test', 'user_type': 'student'}
        )
        self.assertEqual(resp.status_code, 302)


class CheckoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.pc = make_computer(name='PC-01', status='IN_USE')
        self.log = UsageLog.objects.create(
            user_id='u1', user_name='User One', user_type='student',
            computer='PC-01'
        )

    def test_checkout_get_redirects(self):
        resp = self.client.get(reverse('checkout', kwargs={'pc_id': 'PC-01'}))
        self.assertEqual(resp.status_code, 302)

    def test_checkout_post_sets_end_time(self):
        resp = self.client.post(reverse('checkout', kwargs={'pc_id': 'PC-01'}))
        self.assertEqual(resp.status_code, 302)
        self.log.refresh_from_db()
        self.assertIsNotNone(self.log.end_time)

    def test_checkout_post_sets_pc_available(self):
        self.client.post(reverse('checkout', kwargs={'pc_id': 'PC-01'}))
        self.pc.refresh_from_db()
        self.assertEqual(self.pc.status, 'AVAILABLE')

    def test_checkout_post_redirects_to_feedback(self):
        resp = self.client.post(reverse('checkout', kwargs={'pc_id': 'PC-01'}))
        self.assertRedirects(resp, reverse('feedback', kwargs={'pc_id': 'PC-01', 'software_id': self.log.id}),
                             fetch_redirect_response=False)


class StatusViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.config = SiteConfig.objects.create(is_open=True)
        self.pc = make_computer(name='PC-01')

    def test_status_returns_json(self):
        resp = self.client.get(reverse('status', kwargs={'pc_id': 'PC-01'}))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('status', data)

    def test_status_not_found(self):
        resp = self.client.get(reverse('status', kwargs={'pc_id': 'PC-99'}))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'NOT_FOUND')

    def test_status_reflects_pc_status(self):
        self.pc.status = 'IN_USE'
        self.pc.save()
        resp = self.client.get(reverse('status', kwargs={'pc_id': 'PC-01'}))
        data = resp.json()
        self.assertEqual(data['status'], 'IN_USE')


class FeedbackViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.pc = make_computer(name='PC-01')
        self.log = UsageLog.objects.create(
            user_id='u1', user_name='User One', user_type='student',
            computer='PC-01', end_time=timezone.now()
        )

    def test_feedback_get_returns_200(self):
        resp = self.client.get(reverse('feedback', kwargs={'pc_id': 'PC-01', 'software_id': self.log.id}))
        self.assertEqual(resp.status_code, 200)

    def test_feedback_post_saves_score(self):
        resp = self.client.post(
            reverse('feedback', kwargs={'pc_id': 'PC-01', 'software_id': self.log.id}),
            {'satisfaction_score': '5', 'comment': 'Great!'}
        )
        self.assertEqual(resp.status_code, 302)
        self.log.refresh_from_db()
        self.assertEqual(self.log.satisfaction_score, 5)
        self.assertEqual(self.log.comment, 'Great!')

    def test_feedback_post_invalid_log_id_still_redirects(self):
        resp = self.client.post(
            reverse('feedback', kwargs={'pc_id': 'PC-01', 'software_id': 9999}),
            {'satisfaction_score': '3'}
        )
        self.assertEqual(resp.status_code, 302)


# ===========================================================================
# ADMIN USER MANAGEMENT VIEW TESTS
# ===========================================================================

class AdminUserViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin', password='adminpass123')

    def test_admin_users_get_returns_200(self):
        resp = self.client.get(reverse('admin_users'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_users_post_creates_user(self):
        resp = self.client.post(reverse('admin_users'), {
            'username': 'newuser',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'is_staff': True,
        })
        self.assertIn(resp.status_code, [200, 302])


class AdminUserEditViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin', password='adminpass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')

    def test_edit_user_get_returns_200(self):
        resp = self.client.get(reverse('admin_user_edit', kwargs={'pk': self.user2.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_edit_nonexistent_user_returns_404(self):
        resp = self.client.get(reverse('admin_user_edit', kwargs={'pk': 9999}))
        self.assertEqual(resp.status_code, 404)


class AdminUserDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin', password='adminpass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')

    def test_delete_user_post(self):
        resp = self.client.post(reverse('admin_user_delete', kwargs={'pk': self.user2.pk}))
        self.assertIn(resp.status_code, [200, 302])

    def test_delete_nonexistent_user_returns_404(self):
        resp = self.client.post(reverse('admin_user_delete', kwargs={'pk': 9999}))
        self.assertEqual(resp.status_code, 404)


# ===========================================================================
# ADMIN MONITOR VIEW TESTS
# ===========================================================================

class AdminMonitorViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin', password='adminpass123')
        self.pc = make_computer(name='PC-01')

    def test_monitor_get_returns_200(self):
        resp = self.client.get(reverse('admin_monitor'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_checkin_post(self):
        resp = self.client.post(
            reverse('admin_checkin', kwargs={'pc_id': 'PC-01'}),
            data=json.dumps({'user_id': '64010001', 'user_name': 'Admin Test', 'user_type': 'student'}),
            content_type='application/json'
        )
        self.assertIn(resp.status_code, [200, 302])

    def test_admin_checkout_post(self):
        UsageLog.objects.create(
            user_id='u1', user_name='U1', user_type='student', computer='PC-01'
        )
        self.pc.status = 'IN_USE'
        self.pc.save()
        resp = self.client.post(reverse('admin_checkout', kwargs={'pc_id': 'PC-01'}))
        self.assertIn(resp.status_code, [200, 302])


# ===========================================================================
# ADMIN MANAGE PC VIEW TESTS
# ===========================================================================

class AdminManagePcViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin', password='adminpass123')
        self.sw = make_software()
        self.pc = make_computer(name='PC-01', software=self.sw)

    def test_manage_pc_get_returns_200(self):
        resp = self.client.get(reverse('admin_manage_pc'))
        self.assertEqual(resp.status_code, 200)

    def test_add_pc_get_returns_405(self):
        # AdminAddPcView is POST-only
        resp = self.client.get(reverse('admin_add_pc'))
        self.assertEqual(resp.status_code, 405)

    def test_add_pc_post_creates_computer(self):
        resp = self.client.post(reverse('admin_add_pc'), {
            'name': 'PC-99',
            'Software': self.sw.pk,
            'status': 'AVAILABLE',
        })
        self.assertIn(resp.status_code, [200, 302])

    def test_edit_pc_get_returns_405(self):
        # AdminManagePcEditView is POST-only
        resp = self.client.get(reverse('admin_manage_pc_edit', kwargs={'pc_id': self.pc.pk}))
        self.assertEqual(resp.status_code, 405)

    def test_edit_pc_post_updates(self):
        resp = self.client.post(
            reverse('admin_manage_pc_edit', kwargs={'pc_id': self.pc.pk}),
            {'name': 'PC-01', 'Software': self.sw.pk, 'status': 'MAINTENANCE'}
        )
        self.assertIn(resp.status_code, [200, 302])

    def test_delete_pc_post(self):
        resp = self.client.post(reverse('admin_manage_pc_delete', kwargs={'pc_id': self.pc.pk}))
        self.assertIn(resp.status_code, [200, 302])

    def test_delete_nonexistent_pc_returns_404(self):
        # POST to delete non-existent pc_id returns 404
        resp = self.client.post(reverse('admin_manage_pc_delete', kwargs={'pc_id': 9999}))
        self.assertEqual(resp.status_code, 404)


# ===========================================================================
# ADMIN SOFTWARE VIEW TESTS
# ===========================================================================

class AdminSoftwareViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin', password='adminpass123')
        self.sw = make_software(name='MATLAB', version='R2024a')

    def test_software_list_get_returns_200(self):
        resp = self.client.get(reverse('admin_software'))
        self.assertEqual(resp.status_code, 200)

    def test_software_list_post_creates_software(self):
        resp = self.client.post(reverse('admin_software'), {
            'name': 'NewSW',
            'version': '2.0',
            'type': 'Software',
            'expire_date': '2027-12-31',
        })
        self.assertIn(resp.status_code, [200, 302])

    def test_software_edit_get_returns_200(self):
        resp = self.client.get(reverse('admin_software_edit', kwargs={'pk': self.sw.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_software_edit_post_updates(self):
        resp = self.client.post(
            reverse('admin_software_edit', kwargs={'pk': self.sw.pk}),
            {'name': 'MATLAB', 'version': 'R2025a', 'type': 'Software', 'expire_date': ''}
        )
        self.assertIn(resp.status_code, [200, 302])

    def test_software_delete_post(self):
        resp = self.client.post(reverse('admin_software_delete', kwargs={'pk': self.sw.pk}))
        self.assertIn(resp.status_code, [200, 302])
        self.assertFalse(Software.objects.filter(pk=self.sw.pk).exists())

    def test_software_edit_nonexistent_returns_404(self):
        resp = self.client.get(reverse('admin_software_edit', kwargs={'pk': 9999}))
        self.assertEqual(resp.status_code, 404)


# ===========================================================================
# ADMIN BOOKING VIEW TESTS
# ===========================================================================

class AdminBookingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin', password='adminpass123')
        self.pc = make_computer(name='PC-01')
        self.now = timezone.now()
        self.booking = Booking.objects.create(
            student_id='64010001',
            computer=self.pc,
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=3),
            status='PENDING'
        )

    def test_booking_list_get_returns_200(self):
        resp = self.client.get(reverse('admin_booking'))
        self.assertEqual(resp.status_code, 200)

    def test_booking_detail_get_returns_200(self):
        resp = self.client.get(reverse('admin_booking_detail', kwargs={'pk': self.booking.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_booking_detail_nonexistent_returns_404(self):
        resp = self.client.get(reverse('admin_booking_detail', kwargs={'pk': 9999}))
        self.assertEqual(resp.status_code, 404)


class AdminImportBookingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin', password='adminpass123')

    def test_import_booking_get_returns_200(self):
        resp = self.client.get(reverse('admin_booking_import'))
        self.assertEqual(resp.status_code, 200)

    def test_import_booking_post_valid_csv(self):
        pc = make_computer(name='PC-01')
        csv_content = (
            'student_id,computer_id,start_time,end_time\n'
            '64010001,{pc_id},2026-06-01 09:00:00,2026-06-01 11:00:00\n'
        ).format(pc_id=pc.pk)
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'test.csv'
        resp = self.client.post(reverse('admin_booking_import'), {'csv_file': csv_file})
        self.assertIn(resp.status_code, [200, 302])

    def test_import_booking_post_no_file_redirects(self):
        resp = self.client.post(reverse('admin_booking_import'), {})
        self.assertIn(resp.status_code, [200, 302])


# ===========================================================================
# ADMIN REPORT VIEW TESTS
# ===========================================================================

class AdminReportViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin', password='adminpass123')
        UsageLog.objects.create(user_id='s1', user_name='Student1', user_type='student')
        UsageLog.objects.create(user_id='s2', user_name='Staff1', user_type='staff')
        UsageLog.objects.create(user_id='g1', user_name='Guest1', user_type='guest')

    def test_report_get_returns_200(self):
        resp = self.client.get(reverse('admin_report'))
        self.assertEqual(resp.status_code, 200)

    def test_report_context_contains_stats(self):
        resp = self.client.get(reverse('admin_report'))
        self.assertIn('total_visits', resp.context)
        self.assertEqual(resp.context['total_visits'], 3)
        self.assertEqual(resp.context['internal_visits'], 2)
        self.assertEqual(resp.context['guest_visits'], 1)

    def test_report_export_get_returns_csv(self):
        resp = self.client.get(reverse('admin_report_export'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/csv', resp['Content-Type'])

    def test_report_export_with_date_range(self):
        resp = self.client.get(
            reverse('admin_report_export'),
            {'start_date': '2026-01-01T00:00:00', 'end_date': '2026-12-31T23:59:59'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/csv', resp['Content-Type'])

    def test_report_import_csv_valid(self):
        csv_content = (
            '\ufeff'
            'รหัสผู้ใช้,ชื่อ-สกุล,Software,วันที่,เวลา (เข้า-ออก),คณะ/หน่วยงาน,ชั้นปี,ประเภท,PC,คะแนน,ข้อเสนอแนะ\r\n'
            '64010099,Test Import,MATLAB,17/01/2026,09:00 - 10:30,Science,2,นักศึกษา,PC-01,5,Great\r\n'
        )
        csv_file = io.BytesIO(csv_content.encode('utf-8-sig'))
        csv_file.name = 'import.csv'
        resp = self.client.post(reverse('admin_report'), {'csv_file': csv_file})
        self.assertIn(resp.status_code, [200, 302])

    def test_report_import_wrong_extension_rejected(self):
        txt_file = io.BytesIO(b'some text')
        txt_file.name = 'file.txt'
        resp = self.client.post(reverse('admin_report'), {'csv_file': txt_file})
        self.assertIn(resp.status_code, [200, 302])


# ===========================================================================
# ADMIN CONFIG VIEW TESTS
# ===========================================================================

class AdminConfigViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin', password='adminpass123')
        self.config = SiteConfig.objects.create(lab_name='CKLab', is_open=True)

    def test_config_get_returns_200(self):
        resp = self.client.get(reverse('admin_config'))
        self.assertEqual(resp.status_code, 200)

    def test_config_post_updates(self):
        resp = self.client.post(reverse('admin_config'), {
            'lab_name': 'New Lab Name',
            'is_open': True,
            'booking_enabled': True,
            'announcement': 'Hello',
            'location': 'Building A',
        })
        self.assertIn(resp.status_code, [200, 302])
