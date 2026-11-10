import io
import json
from datetime import date, timedelta
from decimal import Decimal
from zipfile import ZipFile

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import Client, TestCase

from .choices import UserRole
from .models import (Assignment, AuditLog, Department, Discipline, Grade, Group, Profile,
                     Semester, Specialty, Student, Teacher, Teaching)


class RequirementsTests(TestCase):
    """Небольшие независимые проверки основных требований лабораторной работы."""

    @classmethod
    def setUpTestData(cls):
        cls.specialty = Specialty.objects.create(code='09.03.01', name='Информатика')
        cls.department = Department.objects.create(name='Кафедра информатики')
        cls.semester = Semester.objects.create(start_year=2026, number=1)
        cls.group = Group.objects.create(name='ИВТ-26', specialty=cls.specialty, course=1, mode_of_study='full-time', admission_year=2026)
        cls.other_group = Group.objects.create(name='ИС-26', specialty=cls.specialty, course=2, mode_of_study='part-time', admission_year=2026)
        cls.users = {}
        for role in ('admin', 'deans_office', 'teacher', 'student'):
            user = User.objects.create_user(role, password='test-password', is_staff=role == 'admin', is_superuser=role == 'admin')
            if role != 'admin':
                Profile.objects.create(user=user, role=role)
            cls.users[role] = user
        cls.foreign_user = User.objects.create_user('foreign_teacher')
        Profile.objects.create(user=cls.foreign_user, role='teacher')
        cls.teacher = Teacher.objects.create(last_name='Иванов', first_name='Иван', department=cls.department, position='professor', academic_degree='', email='teacher@example.test', user=cls.users['teacher'])
        cls.foreign_teacher = Teacher.objects.create(last_name='Петров', first_name='Пётр', department=cls.department, position='assistant', email='other@example.test', user=cls.foreign_user)
        cls.student = Student.objects.create(last_name='Иванов', first_name='Алексей', date_of_birth=date(2006, 1, 1), email='student@example.test', group=cls.group, education_form='budget', user=cls.users['student'])
        cls.peer = Student.objects.create(last_name='Петрова', first_name='Анна', date_of_birth=date(2006, 1, 2), email='peer@example.test', group=cls.group, education_form='contract')
        cls.other_student = Student.objects.create(last_name='Сидоров', first_name='Егор', date_of_birth=date(2006, 1, 3), email='other-student@example.test', group=cls.other_group, education_form='budget')
        cls.discipline = Discipline.objects.create(name='Программирование', control_form='exam')
        cls.credit = Discipline.objects.create(name='Иностранный язык', control_form='credit')
        cls.teaching = Teaching.objects.create(group=cls.group, discipline=cls.discipline, semester=cls.semester, teacher=cls.teacher)
        cls.credit_teaching = Teaching.objects.create(group=cls.group, discipline=cls.credit, semester=cls.semester, teacher=cls.teacher)
        cls.foreign_teaching = Teaching.objects.create(group=cls.other_group, discipline=cls.discipline, semester=cls.semester, teacher=cls.foreign_teacher)
        cls.assignment = Assignment.objects.create(teaching=cls.teaching, title='Лабораторная №1', grade_type='intermediate', weight=1)
        cls.heavy_assignment = Assignment.objects.create(teaching=cls.teaching, title='Контрольная', grade_type='intermediate', weight=3)
        cls.credit_assignment = Assignment.objects.create(teaching=cls.credit_teaching, title='Зачёт', grade_type='final', weight=1)
        cls.foreign_assignment = Assignment.objects.create(teaching=cls.foreign_teaching, title='Чужая работа', grade_type='intermediate', weight=1)

    def as_role(self, role='deans_office'):
        self.client.force_login(self.users[role])

    def send(self, url, data, method='post', client=None):
        return getattr(client or self.client, method)(url, data=json.dumps(data), content_type='application/json')

    def grade(self, value='5', assignment=None, student=None):
        return self.send('/api/journal/grade/', {'student_id': (student or self.student).pk, 'assignment_id': (assignment or self.assignment).pk, 'value': value})

    def group_payload(self):
        return {'name': 'Новая группа', 'course': 1, 'form': 'full-time', 'admissionYear': 2026, 'specialty': self.specialty.pk, 'curator_id': self.teacher.pk}

    def test_01_login_success(self):
        r = self.send('/api/login/', {'username': 'teacher', 'password': 'test-password'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['role'], 'teacher')

    def test_02_login_wrong_password(self):
        self.assertEqual(self.send('/api/login/', {'username': 'teacher', 'password': 'wrong'}).status_code, 401)

    def test_03_superuser_without_profile(self):
        self.assertEqual(self.send('/api/login/', {'username': 'admin', 'password': 'test-password'}).json()['role'], 'admin')
        self.assertEqual(self.client.get('/api/students/').status_code, 200)

    def test_04_user_without_role_denied(self):
        User.objects.create_user('unassigned', password='test-password')
        self.assertEqual(self.send('/api/login/', {'username': 'unassigned', 'password': 'test-password'}).status_code, 403)

    def test_05_logout(self):
        self.as_role('teacher')
        self.assertEqual(self.client.post('/api/logout/').status_code, 200)
        self.assertEqual(self.client.get('/api/me/').status_code, 401)

    def test_06_anonymous_cannot_read_journal(self):
        self.assertEqual(self.client.get(f'/api/journal/{self.teaching.pk}/').status_code, 401)

    def test_07_anonymous_cannot_change_groups(self):
        self.assertEqual(self.send('/api/groups/', self.group_payload()).status_code, 401)
        self.assertEqual(self.client.delete(f'/api/groups/{self.group.pk}/').status_code, 401)

    def test_08_student_cannot_read_peer_journal(self):
        self.as_role('student')
        self.assertEqual(self.client.get(f'/api/journal/{self.teaching.pk}/').status_code, 403)
        self.assertEqual(self.client.get('/api/students/').status_code, 403)

    def test_09_teacher_sees_own_teachings(self):
        self.as_role('teacher')
        ids = [row['id'] for row in self.client.get('/api/teacher/disciplines/').json()]
        self.assertIn(self.teaching.pk, ids)
        self.assertNotIn(self.foreign_teaching.pk, ids)

    def test_10_foreign_journal_denied(self):
        self.as_role('teacher')
        self.assertEqual(self.client.get(f'/api/journal/{self.foreign_teaching.pk}/').status_code, 403)

    def test_11_foreign_grade_denied(self):
        self.as_role('teacher')
        self.assertEqual(self.grade(assignment=self.foreign_assignment, student=self.other_student).status_code, 403)
        self.assertFalse(Grade.objects.exists())

    def test_12_foreign_assignment_change_denied(self):
        self.as_role('teacher')
        url = f'/api/assignments/{self.foreign_assignment.pk}/'
        self.assertEqual(self.send(url, {'title': 'Изменено'}, 'put').status_code, 403)
        self.assertEqual(self.client.delete(url).status_code, 403)

    def test_13_group_create_with_curator(self):
        self.as_role()
        r = self.send('/api/groups/', self.group_payload())
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Group.objects.get(pk=r.json()['id']).curator_id, self.teacher.pk)

    def test_14_group_update(self):
        self.as_role()
        r = self.send(f'/api/groups/{self.group.pk}/', {'name': 'Новое название'}, 'put')
        self.assertEqual(r.status_code, 200)
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'Новое название')

    def test_15_group_delete_without_dependencies(self):
        self.as_role()
        group = Group.objects.create(name='Пустая', specialty=self.specialty, course=1, mode_of_study='full-time', admission_year=2026)
        self.assertEqual(self.client.delete(f'/api/groups/{group.pk}/').status_code, 200)
        self.assertFalse(Group.objects.filter(pk=group.pk).exists())

    def test_16_group_delete_protected(self):
        self.as_role()
        self.assertEqual(self.client.delete(f'/api/groups/{self.group.pk}/').status_code, 400)
        self.assertTrue(Group.objects.filter(pk=self.group.pk).exists())

    def test_17_invalid_course_rejected(self):
        self.as_role()
        payload = self.group_payload()
        payload['course'] = 7
        self.assertEqual(self.send('/api/groups/', payload).status_code, 400)

    def test_18_reference_crud(self):
        self.as_role()
        for kind, payload in [('specialities', {'code': '01.01.01', 'name': 'Новая специальность'}), ('departments', {'name': 'Новая кафедра'}), ('semesters', {'start_year': 2027, 'number': 2})]:
            with self.subTest(reference=kind):
                url = '/api/references/' + kind + '/'
                r = self.send(url, payload)
                self.assertEqual(r.status_code, 200)
                detail = url + str(r.json()['id']) + '/'
                self.assertEqual(self.send(detail, payload, 'put').status_code, 200)
                self.assertEqual(self.client.delete(detail).status_code, 200)

    def test_19_student_create(self):
        self.as_role()
        r = self.send('/api/students/', {'last_name': 'Новый', 'first_name': 'Студент', 'date_of_birth': '2007-01-01', 'gender': 'M', 'email': 'new@example.test', 'education_form': 'budget', 'group_id': self.group.pk})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(Student.objects.filter(pk=r.json()['id']).exists())

    def test_20_invalid_email_rejected(self):
        self.as_role()
        self.assertEqual(self.send(f'/api/students/{self.student.pk}/', {'email': 'не email'}, 'put').status_code, 400)

    def test_21_future_birth_date_rejected(self):
        self.as_role()
        future = (date.today() + timedelta(days=1)).isoformat()
        self.assertEqual(self.send(f'/api/students/{self.student.pk}/', {'date_of_birth': future}, 'put').status_code, 400)

    def test_22_teacher_without_middle_name_or_degree(self):
        self.as_role()
        r = self.send('/api/teachers/', {'last_name': 'Новый', 'first_name': 'Преподаватель', 'department_id': self.department.pk, 'position': 'assistant', 'academic_degree': '', 'email': 'new-teacher@example.test'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get('/api/teachers/').status_code, 200)

    def test_23_discipline_crud(self):
        self.as_role()
        r = self.send('/api/disciplines/', {'name': 'Новый предмет', 'control_form': 'exam', 'hours_lecture': 12})
        self.assertEqual(r.status_code, 200)
        url = f"/api/disciplines/{r.json()['id']}/"
        self.assertEqual(self.send(url, {'hours_lecture': 24}, 'put').status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 200)

    def test_24_teaching_assignment(self):
        self.as_role()
        r = self.send('/api/teachings/', {'group_id': self.other_group.pk, 'discipline_id': self.credit.pk, 'teacher_id': self.teacher.pk, 'semester_id': self.semester.pk})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.delete(f"/api/teachings/{r.json()['id']}/").status_code, 200)

    def test_25_fractional_weight_preserved(self):
        self.as_role('teacher')
        r = self.send(f'/api/teachings/{self.teaching.pk}/assignments/', {'title': 'Дробный вес', 'grade_type': 'intermediate', 'weight': '0.30'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Assignment.objects.get(pk=r.json()['id']).weight, Decimal('0.30'))

    def test_26_zero_weight_rejected(self):
        self.as_role('teacher')
        self.assertEqual(self.send(f'/api/teachings/{self.teaching.pk}/assignments/', {'title': 'Вес 0', 'grade_type': 'intermediate', 'weight': 0}).status_code, 400)

    def test_27_grade_save_and_update(self):
        self.as_role('teacher')
        self.assertEqual(self.grade('4').status_code, 200)
        self.assertEqual(self.grade('5').status_code, 200)
        self.assertEqual(Grade.objects.get(student=self.student, assignment=self.assignment).value, '5')
        self.assertEqual(Grade.objects.count(), 1)

    def test_28_grade_delete(self):
        self.as_role('teacher')
        self.grade('4')
        self.assertEqual(self.grade('').status_code, 200)
        self.assertFalse(Grade.objects.exists())

    def test_29_invalid_grade_rejected(self):
        self.as_role('teacher')
        for value in ('1', '6', 'abc', '4.5', None, '<script>'):
            with self.subTest(value=value):
                self.assertEqual(self.grade(value).status_code, 400)
        self.assertFalse(Grade.objects.exists())

    def test_30_grade_for_wrong_group_rejected(self):
        self.as_role('teacher')
        self.assertEqual(self.grade(student=self.other_student).status_code, 400)

    def test_31_weighted_final_and_rounding(self):
        self.as_role('teacher')
        self.grade('5')
        r = self.grade('2', assignment=self.heavy_assignment)
        self.assertEqual(r.json()['weighted_average'], 2.75)
        self.assertEqual(r.json()['final_grade'], 3)
        journal = self.client.get(f'/api/journal/{self.teaching.pk}/').json()
        self.assertEqual(next(s for s in journal['students'] if s['id'] == self.student.pk)['final_grade'], 3)

    def test_32_credit_pass(self):
        self.as_role('teacher')
        self.assertEqual(self.grade('pass', assignment=self.credit_assignment).json()['final_grade'], 'pass')

    def test_33_credit_fail_in_debtors(self):
        self.as_role('teacher')
        self.grade('fail', assignment=self.credit_assignment)
        self.as_role()
        rows = self.client.get('/api/reports/debtors/').json()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['final_grade'], 'fail')

    def test_34_control_form_validated(self):
        self.as_role('teacher')
        self.assertEqual(self.grade('pass').status_code, 400)
        self.assertEqual(self.grade('5', assignment=self.credit_assignment).status_code, 400)

    def test_35_student_diary_private(self):
        Grade.objects.create(student=self.student, assignment=self.assignment, value='5')
        Grade.objects.create(student=self.peer, assignment=self.assignment, value='2')
        self.as_role('student')
        rows = self.client.get('/api/student/diary/').json()
        row = next(r for r in rows if r['teaching_id'] == self.teaching.pk)
        self.assertEqual(row['grades'], {str(self.assignment.pk): '5'})
        self.assertNotIn('students', row)

    def test_36_own_rating_without_peer_details(self):
        Grade.objects.create(student=self.student, assignment=self.assignment, value='5')
        Grade.objects.create(student=self.peer, assignment=self.assignment, value='4')
        self.as_role('student')
        r = self.client.get('/api/student/rating/').json()
        self.assertEqual(r['place'], 1)
        self.assertEqual(r['avg_grade'], 5)
        self.assertNotIn('students', r)
        self.assertNotIn(str(self.peer), json.dumps(r, ensure_ascii=False))

    def test_37_history_after_group_transfer(self):
        Grade.objects.create(student=self.student, assignment=self.assignment, value='5')
        self.student.group = self.other_group
        self.student.save()
        self.as_role()
        rows = self.client.get('/api/reports/student-summary/', {'student_id': self.student.pk}).json()['results']
        old = next(r for r in rows if r['group'] == self.group.name and r['discipline'] == self.discipline.name)
        self.assertEqual(old['final_grade'], 5)
        self.as_role('student')
        self.assertIn(self.teaching.pk, [r['teaching_id'] for r in self.client.get('/api/student/diary/').json()])

    def test_38_quality_requires_all_good_grades(self):
        Grade.objects.create(student=self.student, assignment=self.assignment, value='5')
        Grade.objects.create(student=self.student, assignment=self.credit_assignment, value='fail')
        self.as_role()
        row = self.client.get('/api/reports/quality/', {'group_id': self.group.pk}).json()[0]
        self.assertEqual(row['good'], 0)
        self.assertEqual(row['quality_percent'], 0)

    def test_39_all_report_pages_render(self):
        self.as_role()
        for slug in ('statement', 'student-summary', 'group-rating', 'debtors', 'statistics', 'quality'):
            with self.subTest(report=slug):
                self.assertEqual(self.client.get('/reports/' + slug + '/').status_code, 200)

    def test_40_all_report_apis(self):
        self.as_role()
        params = [('statement', {'teaching_id': self.teaching.pk}), ('student-summary', {'student_id': self.student.pk}), ('group-rating', {'group_id': self.group.pk}), ('debtors', {}), ('statistics', {'by': 'specialty'}), ('quality', {})]
        for slug, query in params:
            with self.subTest(report=slug):
                self.assertEqual(self.client.get('/api/reports/' + slug + '/', query).status_code, 200)

    def test_41_excel_exports(self):
        self.as_role()
        params = [('statement', {'teaching_id': self.teaching.pk}), ('student-summary', {'student_id': self.student.pk}), ('group-rating', {'group_id': self.group.pk}), ('debtors', {}), ('statistics', {}), ('quality', {})]
        for slug, query in params:
            with self.subTest(report=slug):
                r = self.client.get('/api/reports/' + slug + '/', dict(query, format='xlsx'))
                self.assertEqual(r.status_code, 200)
                self.assertIn('spreadsheetml', r['Content-Type'])
                with ZipFile(io.BytesIO(r.content)) as archive:
                    self.assertIn('xl/worksheets/sheet1.xml', archive.namelist())

    def test_42_audit_records_successful_changes(self):
        self.as_role()
        self.send('/api/groups/', self.group_payload())
        log = AuditLog.objects.get()
        self.assertEqual(log.user_id, self.users['deans_office'].pk)
        self.assertEqual(log.action, 'Создание')
        self.assertEqual(log.path, '/api/groups/')

    def test_43_failed_change_not_logged_as_success(self):
        self.as_role('teacher')
        self.grade('6')
        self.assertFalse(AuditLog.objects.exists())

    def test_44_backup_admin_only(self):
        self.as_role('teacher')
        self.assertEqual(self.client.post('/api/admin/backup/').status_code, 403)
        self.as_role('admin')
        r = self.client.post('/api/admin/backup/')
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertTrue(any(row['model'] == 'education.student' for row in data))
        self.assertFalse(any(row['model'] == 'sessions.session' for row in data))

    def test_45_csrf_required_for_changes(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.users['deans_office'])
        self.assertEqual(self.send('/api/groups/', self.group_payload(), client=client).status_code, 403)
        client.get('/groups/')
        token = client.cookies['csrftoken'].value
        r = client.post('/api/groups/', data=json.dumps(self.group_payload()), content_type='application/json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(r.status_code, 200)

    def test_46_filters(self):
        self.as_role()
        self.assertEqual(len(self.client.get('/api/groups/', {'course': 2}).json()), 1)
        self.assertEqual(len(self.client.get('/api/students/', {'group': self.other_group.pk}).json()), 1)
        self.assertEqual(self.client.get('/api/disciplines/', {'search': 'Нет такого'}).json(), [])

    def test_47_student_card_and_root_routes(self):
        self.assertRedirects(self.client.get('/'), '/login/')
        self.as_role()
        self.assertRedirects(self.client.get('/'), '/home/')
        self.assertEqual(self.client.get(f'/students/{self.student.pk}/card/').status_code, 200)

    def test_48_bad_json_and_methods(self):
        self.as_role()
        self.assertEqual(self.client.post('/api/groups/', data='broken', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.patch('/api/groups/').status_code, 405)
        self.assertEqual(self.client.get('/api/students/999999/').status_code, 404)

    def test_49_duplicate_and_invalid_foreign_key(self):
        self.as_role()
        payload = self.group_payload()
        payload['name'] = self.group.name
        self.assertEqual(self.send('/api/groups/', payload).status_code, 400)
        payload['name'], payload['specialty'] = 'Другая', 999999
        self.assertEqual(self.send('/api/groups/', payload).status_code, 400)

    def test_50_teaching_history_cannot_be_reassigned(self):
        Grade.objects.create(student=self.student, assignment=self.assignment, value='5')
        self.as_role()
        self.assertEqual(self.send(f'/api/teachings/{self.teaching.pk}/', {'group_id': self.other_group.pk}, 'put').status_code, 400)

    def test_51_invalid_grade_database_constraint(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Grade.objects.create(student=self.student, assignment=self.assignment, value='6')

    def test_52_empty_grades_not_zero(self):
        self.as_role('student')
        self.assertIsNone(self.client.get('/api/student/rating/').json()['avg_grade'])
        self.assertIsNone(self.client.get('/api/student/rating/').json()['place'])

    def test_53_admin_can_open_every_directory(self):
        self.as_role('admin')
        for path in ('groups', 'students', 'teachers', 'disciplines', 'teachings', 'specialties', 'departments', 'semesters', 'administration'):
            with self.subTest(page=path):
                self.assertEqual(self.client.get('/' + path + '/').status_code, 200)

    def test_56_admin_role_has_account_management(self):
        user = User.objects.create_user('role_admin', password='test-password')
        Profile.objects.create(user=user, role='admin')
        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.client.force_login(user)
        self.assertEqual(self.client.get('/admin/auth/user/').status_code, 200)

    def test_57_teacher_cannot_enter_admin_even_with_staff_flag(self):
        teacher_user = self.users['teacher']
        teacher_user.is_staff = True
        teacher_user.save()
        self.as_role('teacher')
        self.assertEqual(self.client.get('/admin/').status_code, 302)

    def test_58_student_without_grades_can_be_deleted(self):
        self.as_role()
        r = self.client.delete(f'/api/students/{self.peer.pk}/')
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Student.objects.filter(pk=self.peer.pk).exists())
        self.assertTrue(Student.objects.filter(pk=self.student.pk).exists())

    def test_59_student_with_grades_cannot_be_deleted(self):
        grade = Grade.objects.create(student=self.student, assignment=self.assignment, value='5')
        self.as_role()
        r = self.client.delete(f'/api/students/{self.student.pk}/')
        self.assertEqual(r.status_code, 409)
        self.assertIn('есть оценки', r.json()['error'])
        self.assertIn('Отчислен', r.json()['error'])
        self.assertTrue(Student.objects.filter(pk=self.student.pk).exists())
        self.assertTrue(Grade.objects.filter(pk=grade.pk).exists())
        self.assertFalse(AuditLog.objects.exists())

    def test_60_student_deletion_requires_manager_role(self):
        for role in ('teacher', 'student'):
            with self.subTest(role=role):
                self.as_role(role)
                self.assertEqual(self.client.delete(f'/api/students/{self.peer.pk}/').status_code, 403)
        self.assertTrue(Student.objects.filter(pk=self.peer.pk).exists())


class DemoDataTests(TestCase):
    def test_54_seed_meets_minimum_and_is_repeatable(self):
        call_command('seed_data', stdout=io.StringIO())
        models = (Student, Group, Discipline, Teacher, Grade)
        counts = [model.objects.count() for model in models]
        for actual, minimum in zip(counts, (20, 5, 15, 10, 200)):
            self.assertGreaterEqual(actual, minimum)
        call_command('seed_data', stdout=io.StringIO())
        self.assertEqual(counts, [model.objects.count() for model in models])

    def test_55_created_accounts_can_login(self):
        call_command('seed_data', stdout=io.StringIO())
        call_command('create_accounts', stdout=io.StringIO())
        student = Student.objects.first()
        self.assertIsNotNone(student.user_id)
        self.assertEqual(student.user.profile.role, UserRole.STUDENT)
        self.assertTrue(self.client.login(username=student.email, password='change_password123'))
