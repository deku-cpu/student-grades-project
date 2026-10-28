from django.shortcuts import render
from .api import *

def login_page(request):
    return render(request, 'education/login.html')

from education.choices import GroupStatus, EducationForm,StudentStatus,Gender, PositionStatus, AcademicDegreeStatus
from education.models import Specialty

def groups_page(request):
    # Передаем в шаблон все варианты форм обучения из choices.py
    # (очная, заочная и т.д.)
    return render(request, 'education/groups.html', {
        'group_modes': GroupStatus.choices,
        'courses': range(1, 5), # Создаем список [1, 2, 3, 4] для курсов
        'specialties': Specialty.objects.all()
    })

def teacher_disciplines_page(request):
    return render(request, 'education/teacher/disciplines.html', {
        'courses': range(1, 7) # Передаем список [1, 2, 3, 4, 5, 6]
    })

def journal_page(request, teaching_id):
    return render(request, 'education/journal.html', {'teaching_id': teaching_id})

def students_page(request):
    return render(request, 'education/students.html', {
        'groups': Group.objects.all(),
        'education_forms': EducationForm.choices,
        'statuses': StudentStatus.choices,
        'genders': Gender.choices
    })


def teachers_page(request):
    return render(request, 'education/teachers.html', {
        'departments': Department.objects.all(),
        'positions': PositionStatus.choices,
        'degrees': AcademicDegreeStatus.choices
    })


from education.models import Group, Discipline, Teacher, Semester

def teachings_page(request):
    return render(request, 'education/teachings.html', {
        'groups': Group.objects.all(),
        'disciplines': Discipline.objects.all(),
        'teachers': Teacher.objects.all(),
        'semesters': Semester.objects.all()
    })
from education.choices import GradeType

def assignments_page(request, teaching_id):
    return render(request, 'education/assignments.html', {
        'teaching_id': teaching_id,
        'grade_types': GradeType.choices
    })

def student_diary_page(request):
    return render(request, 'education/student/diary.html')

from .constants import MAIN_CARDS, REPORT_CARDS

def home(request):
    profile = getattr(request.user, 'profile', None)
    role = profile.role if profile else None

    cards = MAIN_CARDS.get(role, [])
    # не пустые 
    cards = [card for card in cards if card[1]]

    # Отчёты показываем только деканату
    reports = []
    if role == UserRole.DEANS_OFFICE:  # Убедись, что UserRole импортирован
        reports = REPORT_CARDS

    return render(request, 'education/home.html', {
        'cards': cards,
        'reports': reports
    })

from .choices import ControlForm

def disciplines_page(request):
    return render(request, 'education/dean/disciplines.html', {
        'control_forms': ControlForm.choices
    })



def report_statement_page(request):
    return render(request, 'reports/statement.html')


def report_student_summary_page(request):
    return render(request, 'reports/student_summary.html')


def report_group_rating_page(request):
    return render(request, 'reports/group_rating.html')


def report_debtors_page(request):
    return render(request, 'reports/debtors.html')


def report_statistics_page(request):
    return render(request, 'reports/statistics.html')


def report_quality_page(request):
    return render(request, 'reports/quality.html')
