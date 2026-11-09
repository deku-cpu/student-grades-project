from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Avg
from django.views.decorators.csrf import csrf_exempt
from .models import Group, Student
from django.contrib.auth import authenticate, login, logout
import json
from django.db.models import Count, Q 

from .models import Group, Student, Specialty, Teaching, Assignment, Grade, Teacher, Department,Discipline, Semester
from .choices import UserRole

def speciality_api(request):

    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)

    if request.method == "GET":
        specialties = Specialty.objects.all().values('id','code','name')

        return JsonResponse(list(specialties), safe=False)


def teacher_disciplines_api(request):
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)


    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != UserRole.TEACHER:
        return JsonResponse({'error': 'Доступ только для преподавателей'}, status=403)

    teachings = Teaching.objects.filter(teacher__user=request.user).select_related('group', 'discipline')

    #фильтры
    search_discipline_query = request.GET.get('search_discipline')
    if search_discipline_query:
        teachings = teachings.filter(discipline__name__icontains=search_discipline_query)

    search_group_query = request.GET.get('search_group')
    if search_group_query:
        teachings = teachings.filter(group__name__icontains=search_group_query)

    course_query = request.GET.get('course')
    if course_query:
        teachings = teachings.filter(group__course=course_query)

    data = []
    for t in teachings:
        data.append({
            'id': t.id, 
            'discipline': t.discipline.name,
            'group': t.group.name,
            'course': t.group.course
        })

    return JsonResponse(data, safe=False)   


@csrf_exempt
def groups_api(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
          
            spec = Specialty.objects.get(id=data.get('specialty'))
            
            Group.objects.create(
                name=data['name'], 
                course=data['course'], 
                mode_of_study=data['form'],
                admission_year=data['admissionYear'], 
                specialty=spec
            )
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


    groups = Group.objects.select_related('specialty').annotate(
        students_count=Count('students',distinct=True)
    )

    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)

        if profile and profile.role!=UserRole.DEANS_OFFICE:
            return JsonResponse({'error': 'Доступ ограничен'}, status=401, json_dumps_params={'ensure_ascii': False})

    # Фильтры
    search_query = request.GET.get('search')
    if search_query:
        groups = groups.filter(name__icontains=search_query)
        
    course_query = request.GET.get('course')
    if course_query:
        groups = groups.filter(course=course_query)
        
    form_query = request.GET.get('form')
    if form_query:
        groups = groups.filter(mode_of_study=form_query)

    specialty_query = request.GET.get('specialty')
    if specialty_query:
        groups = groups.filter(specialty_id=specialty_query)

    # Формируем ответ
    groups_data = []
    for group in groups:
        groups_data.append({
            'id': group.id,
            'name': group.name,
            'yearOfStudy': group.course,
            'specialty_id': group.specialty.id, 
            'specialty': group.specialty.name,
            'form': group.mode_of_study,
            'admissionYear': group.admission_year,
            'students': group.students_count,
        })

    return JsonResponse(groups_data, safe=False)


@csrf_exempt
def group_detail_api(request, group_id=None):


    if request.method == 'PUT' and group_id:
        try:
            data = json.loads(request.body)
            g = Group.objects.get(id=group_id)
            
            # Обновляем поля
            g.name = data['name']
            g.course = data['course']
            g.mode_of_study = data['form']
            g.admission_year = data['admissionYear']
            
            # Обновляем специальность по ID
            spec = Specialty.objects.get(id=data.get('specialty'))
            g.specialty = spec
            g.save()
            
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)



    elif request.method == 'DELETE' and group_id:
        try:
            Group.objects.get(id=group_id).delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@csrf_exempt
def login_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request=request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({
                'username' : user.username,
                'role' : user.profile.role,
            })
        else:
            return JsonResponse({'error': 'Неверный логин или пароль'}, status=401, json_dumps_params={'ensure_ascii': False})

    else:
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

def me_api(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'username': request.user.username,
            'role': request.user.profile.role,
        })
    else:
        return JsonResponse({'error': 'Не авторизован'}, status=401)

@csrf_exempt
def logout_api(request):
    if request.method == 'POST':
        logout(request) # Стираем сессию
        return JsonResponse({'ok': True})
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)




def journal_api(request, teaching_id):
    try:
        teaching = Teaching.objects.select_related('group', 'discipline').get(id=teaching_id)
    except Teaching.DoesNotExist:
        return JsonResponse({'error': 'Пара не найдена'}, status=404)

    students = Student.objects.filter(group=teaching.group).order_by('last_name')
    assignments = Assignment.objects.filter(teaching=teaching).order_by('order')

    # Задания отдаем с весами чтобы JS знал на что умножать
    assignments_data = [{'id': a.id, 'title': a.title, 'weight': float(a.weight)} for a in assignments]

    students_data = []
    for s in students:
        grades = Grade.objects.filter(student=s, assignment__in=assignments)
        grade_dict = {g.assignment_id: g.value for g in grades}
        
        students_data.append({
            'id': s.id,
            'full_name': f"{s.last_name} {s.first_name} {s.middle_name}",
            'grades': grade_dict 
        })

    return JsonResponse({
        'group_name': teaching.group.name,
        'discipline_name': teaching.discipline.name,
        'assignments': assignments_data,
        'students': students_data
    })



@csrf_exempt
def grades_api(request):
    if request.method == 'POST':
        # проверка прав
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Не авторизован'}, status=401)
            
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role not in [UserRole.TEACHER, UserRole.DEANS_OFFICE]:
            return JsonResponse({'error': 'Нет прав на выставление оценок'}, status=403)


        data = json.loads(request.body)
        student_id = data.get('student_id')
        assignment_id = data.get('assignment_id')
        value = data.get('value') 

        try:
            
            if value == '':
                # Если препод стер оценку, удаляем её из базы
                Grade.objects.filter(student_id=student_id, assignment_id=assignment_id).delete()
                return JsonResponse({'ok': True, 'message': 'Оценка удалена'})
            else:
                grade, created = Grade.objects.update_or_create(
                    student_id=student_id,
                    assignment_id=assignment_id,
                    defaults={'value': value}
                )
                return JsonResponse({'ok': True, 'message': 'Оценка сохранена'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@csrf_exempt
def students_api(request):

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)
        
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in [UserRole.DEANS_OFFICE]:
        return JsonResponse({'error': 'Нет прав'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            group = Group.objects.get(id=data.get('group_id')) if data.get('group_id') else None
            
            Student.objects.create(
                last_name=data['last_name'],
                first_name=data['first_name'],
                middle_name=data['middle_name'],
                date_of_birth=data['date_of_birth'],
                gender=data['gender'],
                email=data['email'],
                phone_number=data['phone_number'],
                group=group,
                education_form=data['education_form'],
                admission_date=data['admission_date'],
                status=data['status']
            )
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    students = Student.objects.select_related('group').all()

    search = request.GET.get('search')
    if search:
        students = students.filter(
            Q(last_name__icontains=search) | 
            Q(first_name__icontains=search) | 
            Q(middle_name__icontains=search)
        )

    group_id = request.GET.get('group')
    if group_id:
        students = students.filter(group_id=group_id)

    form_query = request.GET.get('form')
    if form_query:
        students = students.filter(education_form=form_query)

    status_query = request.GET.get('status')
    if status_query:
        students = students.filter(status=status_query)

    students_data = []
    for s in students:
        students_data.append({
            'id': s.id,
            'full_name': f"{s.last_name} {s.first_name} {s.middle_name}",
            'last_name': s.last_name,
            'first_name': s.first_name,
            'middle_name': s.middle_name,
            'date_of_birth': s.date_of_birth.strftime('%Y-%m-%d') if s.date_of_birth else '',
            'gender': s.gender,
            'email': s.email,
            'phone_number': s.phone_number,
            'group_id': s.group.id if s.group else '',
            'group_name': s.group.name if s.group else 'Нет',
            'education_form': s.education_form,
            'admission_date': s.admission_date.strftime('%Y-%m-%d') if s.admission_date else '',
            'status': s.status
        })

    return JsonResponse(students_data, safe=False)


@csrf_exempt
def student_detail_api(request, student_id):

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)
        
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in [UserRole.DEANS_OFFICE]:
        return JsonResponse({'error': 'Нет прав'}, status=403)

    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            s = Student.objects.get(id=student_id)
            group = Group.objects.get(id=data.get('group_id')) if data.get('group_id') else None
            
            s.last_name = data['last_name']
            s.first_name = data['first_name']
            s.middle_name = data['middle_name']
            s.date_of_birth = data['date_of_birth']
            s.gender = data['gender']
            s.email = data['email']
            s.phone_number = data['phone_number']
            s.group = group
            s.education_form = data['education_form']
            s.admission_date = data['admission_date']
            s.status = data['status']
            s.save()
            
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            Student.objects.get(id=student_id).delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)




@csrf_exempt
def teachers_api(request):

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)
        
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in [UserRole.DEANS_OFFICE]:
        return JsonResponse({'error': 'Нет прав'}, status=403)

    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            dept = Department.objects.get(id=data.get('department_id')) if data.get('department_id') else None
            
            Teacher.objects.create(
                last_name=data['last_name'],
                first_name=data['first_name'],
                middle_name=data['middle_name'],
                department=dept,
                position=data['position'],
                academic_degree=data['academic_degree'],
                email=data['email'],
                phone_number=data['phone_number']
            )
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    teachers = Teacher.objects.select_related('department').all()

    search = request.GET.get('search')
    if search:
        teachers = teachers.filter(
            Q(last_name__icontains=search) | 
            Q(first_name__icontains=search) | 
            Q(middle_name__icontains=search)
        )

    dept_id = request.GET.get('department')
    if dept_id:
        teachers = teachers.filter(department_id=dept_id)

    position = request.GET.get('position')
    if position:
        teachers = teachers.filter(position=position)

    teachers_data = []
    for t in teachers:
        teachers_data.append({
            'id': t.id,
            'full_name': f"{t.last_name} {t.first_name} {t.middle_name}",
            'last_name': t.last_name,
            'first_name': t.first_name,
            'middle_name': t.middle_name,
            'department_id': t.department.id if t.department else '',
            'department_name': t.department.name if t.department else 'Нет',
            'position': t.position,
            'academic_degree': t.academic_degree,
            'email': t.email,
            'phone_number': t.phone_number
        })

    return JsonResponse(teachers_data, safe=False)


@csrf_exempt
def teacher_detail_api(request, teacher_id):


    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)
        
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in [UserRole.DEANS_OFFICE]:
        return JsonResponse({'error': 'Нет прав'}, status=403)

    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            t = Teacher.objects.get(id=teacher_id)
            dept = Department.objects.get(id=data.get('department_id')) if data.get('department_id') else None
            
            t.last_name = data['last_name']
            t.first_name = data['first_name']
            t.middle_name = data['middle_name']
            t.department = dept
            t.position = data['position']
            t.academic_degree = data['academic_degree']
            t.email = data['email']
            t.phone_number = data['phone_number']
            t.save()
            
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            Teacher.objects.get(id=teacher_id).delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)        




@csrf_exempt
def teachings_api(request):


    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)
        
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in [UserRole.DEANS_OFFICE]:
        return JsonResponse({'error': 'Нет прав'}, status=403)

    # СОЗДАНИЕ
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            group = Group.objects.get(id=data.get('group_id'))
            discipline = Discipline.objects.get(id=data.get('discipline_id'))
            teacher = Teacher.objects.get(id=data.get('teacher_id'))
            semester = Semester.objects.get(id=data.get('semester_id'))
            
            Teaching.objects.create(
                group=group, discipline=discipline, teacher=teacher, semester=semester
            )
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # ЧТЕНИЕ (СПИСОК)
    teachings = Teaching.objects.select_related('group', 'discipline', 'teacher', 'semester').all()

    search = request.GET.get('search')
    if search:
        teachings = teachings.filter(
            Q(group__name__icontains=search) | Q(discipline__name__icontains=search)
        )

    data = []
    for t in teachings:
        data.append({
            'id': t.id,
            'group_id': t.group.id,
            'group_name': t.group.name,
            'discipline_id': t.discipline.id,
            'discipline_name': t.discipline.name,
            'teacher_id': t.teacher.id,
            'teacher_name': f"{t.teacher.last_name} {t.teacher.first_name[0]}.{t.teacher.middle_name[0]}.",
            'semester_id': t.semester.id,
            'semester_name': str(t.semester),
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
def teaching_detail_api(request, teaching_id):


    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)
        
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in [UserRole.DEANS_OFFICE]:
        return JsonResponse({'error': 'Нет прав'}, status=403)

    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            t = Teaching.objects.get(id=teaching_id)
            t.group = Group.objects.get(id=data.get('group_id'))
            t.discipline = Discipline.objects.get(id=data.get('discipline_id'))
            t.teacher = Teacher.objects.get(id=data.get('teacher_id'))
            t.semester = Semester.objects.get(id=data.get('semester_id'))
            t.save()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            Teaching.objects.get(id=teaching_id).delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)





@csrf_exempt
def assignments_api(request, teaching_id):

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)
        
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in [UserRole.DEANS_OFFICE,UserRole.TEACHER]:
        return JsonResponse({'error': 'Нет прав'}, status=403)

    # Проверка что препод - учитель группы 
    if profile.role == UserRole.TEACHER:
        teaching = Teaching.objects.get(id=teaching_id)
        teacher = getattr(request.user, 'teacher_profile', None)
        if (teacher == None or teaching.teacher != teacher):
            return JsonResponse({'error': 'Нет прав'}, status=403)


    # СОЗДАНИЕ
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            teaching = Teaching.objects.get(id=teaching_id)
            
            Assignment.objects.create(
                teaching=teaching,
                title=data['title'],
                grade_type=data['grade_type'],
                weight=data.get('weight', 1),
                order=data.get('order', 0),
                date=data.get('date') or None
            )
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # ЧТЕНИЕ (СПИСОК заданий для конкретной пары)
    assignments = Assignment.objects.filter(teaching_id=teaching_id).order_by('order')
    
    data = []
    for a in assignments:
        data.append({
            'id': a.id,
            'title': a.title,
            'grade_type': a.grade_type,
            'weight': a.weight,
            'order': a.order,
            'date': a.date.strftime('%Y-%m-%d') if a.date else ''
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
def assignment_detail_api(request, assignment_id):

    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)
        
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in [UserRole.DEANS_OFFICE,UserRole.TEACHER]:
        return JsonResponse({'error': 'Нет прав'}, status=403)

    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            a = Assignment.objects.get(id=assignment_id)
            a.title = data['title']
            a.grade_type = data['grade_type']
            a.weight = data.get('weight', 1)
            a.order = data.get('order', 0)
            a.date = data.get('date') or None
            a.save()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            Assignment.objects.get(id=assignment_id).delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)



def student_diary_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != UserRole.STUDENT:
        return JsonResponse({'error': 'Нет прав'}, status=403)


    student = request.user.student_profile

    if not student.group:
        return JsonResponse({'error': 'Вы не привязаны к группе'}, status=400)

    # Ищем все пары для его группы
    teachings = Teaching.objects.filter(group=student.group).select_related('discipline', 'teacher')

    data = []
    for t in teachings:
        
        assignments = Assignment.objects.filter(teaching=t).order_by('order')

        
        grades = Grade.objects.filter(student=student, assignment__in=assignments)
        grade_dict = {g.assignment_id: g.value for g in grades}


        total_score = 0
        total_weight = 0
        for a in assignments:
            val = grade_dict.get(a.id)
            if val and str(val).isdigit():
                total_score += int(val) * a.weight
                total_weight += a.weight

        final_grade = round(total_score / total_weight, 2) if total_weight > 0 else '—'

        data.append({
            'teaching_id': t.id,
            'discipline': t.discipline.name,
            'teacher': f"{t.teacher.last_name} {t.teacher.first_name[0]}.{t.teacher.middle_name[0]}.",
            'assignments': [{'id': a.id, 'title': a.title} for a in assignments],
            'grades': grade_dict,
            'final_grade': final_grade
        })

    return JsonResponse(data, safe=False)



@csrf_exempt
def disciplines_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401, json_dumps_params={'ensure_ascii': False})

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != UserRole.DEANS_OFFICE:
        return JsonResponse({'error': 'Доступ ограничен'}, status=403, json_dumps_params={'ensure_ascii': False})

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            Discipline.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                hours_lecture=data.get('hours_lecture', 0),
                hours_practice=data.get('hours_practice', 0),
                hours_lab=data.get('hours_lab', 0),
                control_form=data['control_form']
            )
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400, json_dumps_params={'ensure_ascii': False})

    # GET запрос (список)
    disciplines = Discipline.objects.all()

    # Фильтры
    search_query = request.GET.get('search')
    if search_query:
        disciplines = disciplines.filter(name__icontains=search_query)
        
    control_query = request.GET.get('control_form')
    if control_query:
        disciplines = disciplines.filter(control_form=control_query)

    # Формируем ответ
    disciplines_data = []
    for d in disciplines:
        disciplines_data.append({
            'id': d.id,
            'name': d.name,
            'description': d.description,
            'hours_lecture': d.hours_lecture,
            'hours_practice': d.hours_practice,
            'hours_lab': d.hours_lab,
            'control_form': d.control_form,
        })

    return JsonResponse(disciplines_data, safe=False)


@csrf_exempt
def discipline_detail_api(request, discipline_id=None):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401, json_dumps_params={'ensure_ascii': False})

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != UserRole.DEANS_OFFICE:
        return JsonResponse({'error': 'Доступ ограничен'}, status=403, json_dumps_params={'ensure_ascii': False})

    if request.method == 'PUT' and discipline_id:
        try:
            data = json.loads(request.body)
            d = Discipline.objects.get(id=discipline_id)
            
            d.name = data['name']
            d.description = data.get('description', '')
            d.hours_lecture = data.get('hours_lecture', 0)
            d.hours_practice = data.get('hours_practice', 0)
            d.hours_lab = data.get('hours_lab', 0)
            d.control_form = data['control_form']
            d.save()
            
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400, json_dumps_params={'ensure_ascii': False})

    elif request.method == 'DELETE' and discipline_id:
        try:
            Discipline.objects.get(id=discipline_id).delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)





def _is_dean(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    p = getattr(user, 'profile', None)
    return bool(p and p.role == UserRole.DEANS_OFFICE)


def _forbidden():
    return JsonResponse(
        {'error': 'Доступ ограничен'},
        status=403,
        json_dumps_params={'ensure_ascii': False},
    )


def _compute_final_from_grades(grades, assignments):
    """Итоговая оценка с учётом весов. grades: {assignment_id: value}"""
    total, weight_sum = 0, 0
    for a in assignments:
        v = grades.get(a.id)
        if v and str(v).isdigit():
            total += int(v) * a.weight
            weight_sum += a.weight
    return round(total / weight_sum, 2) if weight_sum else None


def _final_grade(student, teaching):
    assignments = list(Assignment.objects.filter(teaching=teaching))
    grades = {
        g.assignment_id: g.value
        for g in Grade.objects.filter(student=student, assignment__in=assignments)
    }
    return _compute_final_from_grades(grades, assignments)



def report_statement_api(request):
    """Отчёт 1: Ведомость по группе и дисциплине. Параметр: teaching_id"""
    if not _is_dean(request.user):
        return _forbidden()

    teaching_id = request.GET.get('teaching_id')
    if not teaching_id:
        return JsonResponse({'error': 'Не указан teaching_id'}, status=400,
                            json_dumps_params={'ensure_ascii': False})

    try:
        t = Teaching.objects.select_related('group', 'discipline', 'teacher', 'semester').get(id=teaching_id)
    except Teaching.DoesNotExist:
        return JsonResponse({'error': 'Пара не найдена'}, status=404,
                            json_dumps_params={'ensure_ascii': False})

    assignments = list(Assignment.objects.filter(teaching=t).order_by('order'))
    students = Student.objects.filter(group=t.group).order_by('last_name', 'first_name')

    students_data = []
    finals = []
    for s in students:
        grades = {
            g.assignment_id: g.value
            for g in Grade.objects.filter(student=s, assignment__in=assignments)
        }
        final = _compute_final_from_grades(grades, assignments)
        if final is not None:
            finals.append(final)
        students_data.append({
            'id': s.id,
            'full_name': f"{s.last_name} {s.first_name} {s.middle_name}",
            'grades': grades,
            'final_grade': final,
        })

    avg = round(sum(finals) / len(finals), 2) if finals else None
    quality = round(100 * sum(1 for g in finals if g >= 4) / len(finals), 1) if finals else 0
    absolute = round(100 * sum(1 for g in finals if g >= 3) / len(finals), 1) if finals else 0

    return JsonResponse({
        'group_name': t.group.name,
        'discipline_name': t.discipline.name,
        'control_form': t.discipline.control_form,
        'semester': str(t.semester),
        'teacher': f"{t.teacher.last_name} {t.teacher.first_name[0]}.{t.teacher.middle_name[0]}.",
        'assignments': [{'id': a.id, 'title': a.title, 'weight': a.weight} for a in assignments],
        'students': students_data,
        'avg_grade': avg,
        'quality_percent': quality,
        'absolute_percent': absolute,
    }, json_dumps_params={'ensure_ascii': False})




def report_student_summary_api(request):
    """Отчёт 2: Сводная ведомость по студенту. Параметр: student_id"""
    if not _is_dean(request.user):
        return _forbidden()

    student_id = request.GET.get('student_id')
    if not student_id:
        return JsonResponse({'error': 'Не указан student_id'}, status=400,
                            json_dumps_params={'ensure_ascii': False})

    try:
        s = Student.objects.select_related('group', 'group__specialty').get(id=student_id)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Студент не найден'}, status=404,
                            json_dumps_params={'ensure_ascii': False})

    teachings = (Teaching.objects
                 .filter(group=s.group)
                 .select_related('discipline', 'semester', 'teacher')) if s.group else []

    results = []
    finals = []
    for t in teachings:
        assignments = list(Assignment.objects.filter(teaching=t).order_by('order'))
        grades = {
            g.assignment_id: g.value
            for g in Grade.objects.filter(student=s, assignment__in=assignments)
        }
        final = _compute_final_from_grades(grades, assignments)
        if final is not None:
            finals.append(final)
        results.append({
            'discipline': t.discipline.name,
            'control_form': t.discipline.control_form,
            'semester': str(t.semester),
            'teacher': f"{t.teacher.last_name} {t.teacher.first_name[0]}.{t.teacher.middle_name[0]}.",
            'assignments': [
                {'title': a.title, 'weight': a.weight, 'value': grades.get(a.id)}
                for a in assignments
            ],
            'final_grade': final,
        })

    return JsonResponse({
        'id': s.id,
        'full_name': f"{s.last_name} {s.first_name} {s.middle_name}",
        'group_name': s.group.name if s.group else '',
        'specialty': s.group.specialty.name if s.group else '',
        'course': s.group.course if s.group else None,
        'education_form': s.education_form,
        'status': s.status,
        'results': results,
        'avg_grade': round(sum(finals) / len(finals), 2) if finals else None,
        'bad_count': sum(1 for g in finals if g < 3),
    }, json_dumps_params={'ensure_ascii': False})



def report_group_rating_api(request):
    """Отчёт 3: Рейтинг студентов в группе. Параметр: group_id"""
    if not _is_dean(request.user):
        return _forbidden()

    group_id = request.GET.get('group_id')
    if not group_id:
        return JsonResponse({'error': 'Не указан group_id'}, status=400,
                            json_dumps_params={'ensure_ascii': False})

    try:
        g = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Группа не найдена'}, status=404,
                            json_dumps_params={'ensure_ascii': False})

    teachings = list(Teaching.objects.filter(group=g))
    students = Student.objects.filter(group=g).order_by('last_name', 'first_name')

    data = []
    for s in students:
        finals = [f for f in (_final_grade(s, t) for t in teachings) if f is not None]
        data.append({
            'id': s.id,
            'full_name': f"{s.last_name} {s.first_name} {s.middle_name}",
            'avg_grade': round(sum(finals) / len(finals), 2) if finals else None,
            'bad_count': sum(1 for f in finals if f < 3),
        })

    data.sort(key=lambda x: (x['avg_grade'] is None, -(x['avg_grade'] or 0)))
    for i, row in enumerate(data, 1):
        row['place'] = i

    return JsonResponse({
        'group_name': g.name,
        'students': data,
    }, json_dumps_params={'ensure_ascii': False})



def report_debtors_api(request):
    """Отчёт 4: Должники. Параметр: group_id (опционально)"""
    if not _is_dean(request.user):
        return _forbidden()

    group_id = request.GET.get('group_id')
    students = Student.objects.select_related('group', 'group__specialty')
    if group_id:
        students = students.filter(group_id=group_id)

    data = []
    for s in students:
        if not s.group:
            continue
        teachings = Teaching.objects.filter(group=s.group).select_related('discipline', 'semester')
        for t in teachings:
            f = _final_grade(s, t)
            if f is not None and f < 3:
                data.append({
                    'student': f"{s.last_name} {s.first_name} {s.middle_name}",
                    'group': s.group.name,
                    'discipline': t.discipline.name,
                    'semester': str(t.semester),
                    'final_grade': f,
                })

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})




def report_statistics_api(request):
    """Отчёт 5: Статистика. Параметр by = group | course | specialty"""
    if not _is_dean(request.user):
        return _forbidden()

    by = request.GET.get('by', 'group')
    if by not in ('group', 'course', 'specialty'):
        return JsonResponse({'error': 'by должен быть group | course | specialty'}, status=400,
                            json_dumps_params={'ensure_ascii': False})

    students = Student.objects.select_related('group', 'group__specialty').all()

    buckets = {}
    for s in students:
        if not s.group:
            continue

        if by == 'group':
            key = s.group.name
        elif by == 'course':
            key = f"{s.group.course} курс"
        else:
            key = s.group.specialty.name

        if key not in buckets:
            buckets[key] = {'students': 0, 'grades_sum': 0, 'grades_n': 0, 'bad': 0}

        b = buckets[key]
        b['students'] += 1

        for t in Teaching.objects.filter(group=s.group):
            f = _final_grade(s, t)
            if f is None:
                continue
            b['grades_sum'] += f
            b['grades_n'] += 1
            if f < 3:
                b['bad'] += 1

    result = [{
        'name': key,
        'students': b['students'],
        'avg_grade': round(b['grades_sum'] / b['grades_n'], 2) if b['grades_n'] else None,
        'bad_count': b['bad'],
    } for key, b in buckets.items()]

    result.sort(key=lambda x: x['name'])
    return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})



def report_quality_api(request):
    """Отчёт 6: Качество знаний. Параметр: group_id (опционально)"""
    if not _is_dean(request.user):
        return _forbidden()

    group_id = request.GET.get('group_id')
    students = Student.objects.select_related('group')
    if group_id:
        students = students.filter(group_id=group_id)

    buckets = {}
    for s in students:
        if not s.group:
            continue
        key = s.group.name
        if key not in buckets:
            buckets[key] = {'total': 0, 'good': 0}
        buckets[key]['total'] += 1

        finals = [f for f in (_final_grade(s, t) for t in Teaching.objects.filter(group=s.group)) if f is not None]
        avg = sum(finals) / len(finals) if finals else None
        if avg is not None and avg >= 4:
            buckets[key]['good'] += 1

    result = [{
        'group': key,
        'students': b['total'],
        'good': b['good'],
        'quality_percent': round(100 * b['good'] / b['total'], 1) if b['total'] else 0,
    } for key, b in buckets.items()]

    result.sort(key=lambda x: x['group'])
    return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})