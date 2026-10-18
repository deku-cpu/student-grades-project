from django.shortcuts import render
from .api import *

def login_page(request):
    return render(request, 'education/login.html')

from education.choices import GroupStatus
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