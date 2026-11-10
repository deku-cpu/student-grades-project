from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from .access import check_teaching, page_access, user_role
from .choices import (AcademicDegreeStatus, ControlForm, EducationForm, Gender, GradeType,
                      GroupStatus, PositionStatus, StudentStatus, UserRole)
from .constants import MAIN_CARDS, REPORT_CARDS
from .models import Department, Discipline, Group, Semester, Specialty, Student, Teacher, Teaching


def index(request):
    return redirect('home' if request.user.is_authenticated else 'login_page')


@ensure_csrf_cookie
def login_page(request):
    return render(request, 'education/login.html')


@page_access(*UserRole.values)
def home(request):
    role = user_role(request.user)
    cards = list(MAIN_CARDS.get(role, []))
    if role == UserRole.ADMIN:
        cards = list(MAIN_CARDS[UserRole.DEANS_OFFICE]) + [
            ('Пользователи и роли', 'admin:auth_user_changelist', 'Учётные записи и назначение ролей'),
            ('Администрирование', 'administration_page', 'Журнал действий и резервное копирование'),
        ]
    return render(request, 'education/home.html', {'cards': cards,
                  'reports': REPORT_CARDS if role in (UserRole.ADMIN, UserRole.DEANS_OFFICE) else []})


@page_access(UserRole.DEANS_OFFICE)
def groups_page(request):
    return render(request, 'education/groups.html', {
        'group_modes': GroupStatus.choices, 'courses': range(1, 7),
        'specialties': Specialty.objects.order_by('code'), 'teachers': Teacher.objects.order_by('last_name')})


@page_access(UserRole.TEACHER, UserRole.DEANS_OFFICE)
def teacher_disciplines_page(request):
    return render(request, 'education/teacher/disciplines.html', {'courses': range(1, 7)})


@page_access(UserRole.TEACHER, UserRole.DEANS_OFFICE)
def journal_page(request, teaching_id):
    teaching = get_object_or_404(Teaching.objects.select_related('teacher'), pk=teaching_id)
    check_teaching(request.user, teaching)
    return render(request, 'education/journal.html', {'teaching_id': teaching_id})


@page_access(UserRole.DEANS_OFFICE)
def students_page(request):
    return render(request, 'education/students.html', {'groups': Group.objects.order_by('name'),
        'education_forms': EducationForm.choices, 'statuses': StudentStatus.choices, 'genders': Gender.choices})


@page_access(UserRole.DEANS_OFFICE)
def student_card_page(request, student_id):
    student = get_object_or_404(Student.objects.select_related('group'), pk=student_id)
    return render(request, 'education/student_card.html', {'student': student})


@page_access(UserRole.DEANS_OFFICE)
def teachers_page(request):
    return render(request, 'education/teachers.html', {'departments': Department.objects.order_by('name'),
        'positions': PositionStatus.choices, 'degrees': AcademicDegreeStatus.choices})


@page_access(UserRole.DEANS_OFFICE)
def teachings_page(request):
    return render(request, 'education/teachings.html', {'groups': Group.objects.order_by('name'),
        'disciplines': Discipline.objects.order_by('name'), 'teachers': Teacher.objects.order_by('last_name'),
        'semesters': Semester.objects.order_by('start_year', 'number')})


@page_access(UserRole.TEACHER, UserRole.DEANS_OFFICE)
def assignments_page(request, teaching_id):
    teaching = get_object_or_404(Teaching.objects.select_related('teacher'), pk=teaching_id)
    check_teaching(request.user, teaching)
    return render(request, 'education/assignments.html', {'teaching_id': teaching_id, 'grade_types': GradeType.choices})


@page_access(UserRole.STUDENT)
def student_diary_page(request):
    return render(request, 'education/student/diary.html')


@page_access(UserRole.STUDENT)
def student_rating_page(request):
    return render(request, 'education/student/rating.html')


@page_access(UserRole.DEANS_OFFICE)
def disciplines_page(request):
    return render(request, 'education/dean/disciplines.html', {'control_forms': ControlForm.choices})


REFERENCE_FIELDS = {
    'specialities': ('Специальности', [{'name': 'code', 'label': 'Код', 'type': 'text'}, {'name': 'name', 'label': 'Название', 'type': 'text'}]),
    'departments': ('Кафедры', [{'name': 'name', 'label': 'Название', 'type': 'text'}]),
    'semesters': ('Семестры', [{'name': 'start_year', 'label': 'Год начала', 'type': 'number', 'min': 2000, 'max': 2100}, {'name': 'number', 'label': 'Номер семестра', 'type': 'number', 'min': 1, 'max': 2}]),
}


def reference_page(request, reference):
    title, fields = REFERENCE_FIELDS[reference]
    return render(request, 'education/references.html', {'reference_title': title, 'fields': fields,
                  'reference_config': {'url': '/api/references/' + reference + '/', 'fields': fields}})


@page_access(UserRole.DEANS_OFFICE)
def specialties_page(request):
    return reference_page(request, 'specialities')


@page_access(UserRole.DEANS_OFFICE)
def departments_page(request):
    return reference_page(request, 'departments')


@page_access(UserRole.DEANS_OFFICE)
def semesters_page(request):
    return reference_page(request, 'semesters')


@page_access(UserRole.ADMIN)
def administration_page(request):
    return render(request, 'education/administration.html')


@page_access(UserRole.DEANS_OFFICE)
def report_statement_page(request):
    return render(request, 'education/reports/statement.html')


@page_access(UserRole.DEANS_OFFICE)
def report_student_summary_page(request):
    return render(request, 'education/reports/student_summary.html')


@page_access(UserRole.DEANS_OFFICE)
def report_group_rating_page(request):
    return render(request, 'education/reports/group_rating.html')


@page_access(UserRole.DEANS_OFFICE)
def report_debtors_page(request):
    return render(request, 'education/reports/debtors.html')


@page_access(UserRole.DEANS_OFFICE)
def report_statistics_page(request):
    return render(request, 'education/reports/statistics.html')


@page_access(UserRole.DEANS_OFFICE)
def report_quality_page(request):
    return render(request, 'education/reports/quality.html')
