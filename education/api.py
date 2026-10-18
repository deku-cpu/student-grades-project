from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Avg
from django.views.decorators.csrf import csrf_exempt
from .models import Group, Student
from django.contrib.auth import authenticate, login, logout
import json
from django.db.models import Count, Q 

from .models import Group, Student, Specialty, Teaching, Assignment, Grade 

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
    if not profile or profile.role != 'teacher':
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

        if profile and profile.role == 'student':
            return JsonResponse({'error': 'Доступ ограничен'}, status=401, json_dumps_params={'ensure_ascii': False})
        
        if profile and profile.role == 'teacher':
            groups = groups.filter(
                Q(curator__user=request.user) | Q(teachings__teacher__user=request.user)
            ).distinct()

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
        if not profile or profile.role not in ['teacher', 'deans_office']:
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