from django.http import JsonResponse
from django.db.models import Count
from .models import Group

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