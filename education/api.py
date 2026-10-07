from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Avg
from django.views.decorators.csrf import csrf_exempt
from .models import Group, Student
from django.contrib.auth import authenticate, login
import json

def groups_api(request):
    groups = Group.objects.select_related('specialty').annotate(
        students_count=Count('students')
    )

    groups_data = []

    for group in groups:
        groups_data.append({
            'id': group.id,
            'name': group.name,
            'yearOfStudy': group.course,
            'specialty': group.specialty.name,
            'form': group.mode_of_study,
            'admissionYear': group.admission_year,
            'students': group.students_count,
        })

    return JsonResponse(groups_data, safe=False)

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