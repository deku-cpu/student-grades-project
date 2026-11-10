from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q

from .access import api_access
from .api import response, teacher_name
from .choices import UserRole
from .exports import report_response
from .grading import is_debt, mean_grade, result_for_student, teachings_for_student
from .models import Group, Student, Teaching


def all_teachings():
    return list(Teaching.objects.select_related('group', 'discipline', 'teacher', 'semester')
                .prefetch_related('assignments__grades').order_by('semester__start_year', 'semester__number', 'discipline__name'))


def student_values(student, teachings):
    values = []
    for teaching in teachings:
        final, grades, assignments = result_for_student(student, teaching)
        if teaching.group_id == student.group_id or grades:
            values.append(final)
    return values


def group_rating(group):
    teachings = all_teachings()
    rows = []
    for student in group.students.order_by('last_name', 'first_name', 'id'):
        values = student_values(student, teachings)
        rows.append({'id': student.pk, 'full_name': str(student), 'avg_grade': mean_grade(values),
                     'bad_count': sum(is_debt(v) for v in values)})
    rows.sort(key=lambda row: (row['avg_grade'] is None, -(row['avg_grade'] or 0), row['bad_count'], row['full_name']))
    previous_score, place = None, 0
    for index, row in enumerate(rows, 1):
        score = (row['avg_grade'], row['bad_count'])
        if score != previous_score:
            place = index
        row['place'] = place if row['avg_grade'] is not None else None
        previous_score = score
    return {'group_name': group.name, 'students': rows}


@api_access(UserRole.DEANS_OFFICE)
def report_statement_api(request):
    if not request.GET.get('teaching_id'):
        raise ValidationError('Выберите группу и дисциплину')
    teaching = Teaching.objects.select_related('group', 'discipline', 'teacher', 'semester').prefetch_related('assignments__grades').get(pk=request.GET['teaching_id'])
    assignments = list(teaching.assignments.all())
    students = Student.objects.filter(Q(group=teaching.group) | Q(grade__assignment__teaching=teaching)).distinct().order_by('last_name', 'first_name')
    rows, finals = [], []
    for student in students:
        final, grades, unused = result_for_student(student, teaching)
        finals.append(final)
        rows.append({'id': student.pk, 'full_name': str(student), 'grades': grades, 'final_grade': final})
    count = len(rows)
    data = {'group_name': teaching.group.name, 'discipline_name': teaching.discipline.name,
            'control_form': teaching.discipline.get_control_form_display(), 'semester': str(teaching.semester),
            'teacher': teacher_name(teaching.teacher),
            'assignments': [{'id': a.pk, 'title': a.title, 'weight': float(a.weight)} for a in assignments],
            'students': rows, 'avg_grade': mean_grade(finals),
            'quality_percent': round(100 * sum(isinstance(v, (int, float)) and v >= 4 for v in finals) / count, 1) if count else 0,
            'absolute_percent': round(100 * sum(v is not None and not is_debt(v) for v in finals) / count, 1) if count else 0}
    return report_response(request, data, 'statement')


@api_access(UserRole.DEANS_OFFICE)
def report_student_summary_api(request):
    if not request.GET.get('student_id'):
        raise ValidationError('Выберите студента')
    student = Student.objects.select_related('group__specialty').get(pk=request.GET['student_id'])
    results, values = [], []
    for teaching in teachings_for_student(student):
        final, grades, assignments = result_for_student(student, teaching)
        values.append(final)
        results.append({'discipline': teaching.discipline.name, 'group': teaching.group.name,
                        'control_form': teaching.discipline.get_control_form_display(), 'semester': str(teaching.semester),
                        'teacher': teacher_name(teaching.teacher),
                        'assignments': [{'title': a.title, 'weight': float(a.weight), 'value': grades.get(a.pk)} for a in assignments],
                        'final_grade': final})
    data = {'id': student.pk, 'full_name': str(student), 'group_name': student.group.name if student.group else '',
            'specialty': student.group.specialty.name if student.group else '',
            'course': student.group.course if student.group else None,
            'education_form': student.get_education_form_display(), 'status': student.get_status_display(),
            'results': results, 'avg_grade': mean_grade(values), 'bad_count': sum(is_debt(v) for v in values)}
    return report_response(request, data, 'student-summary')


@api_access(UserRole.DEANS_OFFICE)
def report_group_rating_api(request):
    if not request.GET.get('group_id'):
        raise ValidationError('Выберите группу')
    group = Group.objects.get(pk=request.GET['group_id'])
    return report_response(request, group_rating(group), 'group-rating')


@api_access(UserRole.STUDENT)
def student_rating_api(request):
    student = getattr(request.user, 'student_profile', None)
    if not student or not student.group_id:
        raise ValidationError('Студент не привязан к группе')
    rating = group_rating(student.group)
    own = next(row for row in rating['students'] if row['id'] == student.pk)
    return response(dict(own, group_name=rating['group_name'], students_count=len(rating['students'])))


@api_access(UserRole.DEANS_OFFICE)
def report_debtors_api(request):
    students = Student.objects.select_related('group').order_by('last_name', 'first_name')
    if request.GET.get('group_id'):
        students = students.filter(group_id=request.GET['group_id'])
    teachings = all_teachings()
    rows = []
    for student in students:
        for teaching in teachings:
            final, grades, unused = result_for_student(student, teaching)
            if is_debt(final) and (teaching.group_id == student.group_id or grades):
                rows.append({'student': str(student), 'group': teaching.group.name,
                             'discipline': teaching.discipline.name, 'semester': str(teaching.semester), 'final_grade': final})
    return report_response(request, rows, 'debtors')


@api_access(UserRole.DEANS_OFFICE)
def report_statistics_api(request):
    by = request.GET.get('by', 'group')
    if by not in ('group', 'course', 'specialty'):
        raise ValidationError('Выберите группировку по группам, курсам или специальностям')
    teachings = all_teachings()
    buckets = {}
    for student in Student.objects.select_related('group__specialty').exclude(group=None):
        key = student.group.name if by == 'group' else f'{student.group.course} курс' if by == 'course' else student.group.specialty.name
        bucket = buckets.setdefault(key, {'students': 0, 'values': []})
        bucket['students'] += 1
        bucket['values'] += student_values(student, teachings)
    rows = [{'name': name, 'students': bucket['students'], 'avg_grade': mean_grade(bucket['values']),
             'bad_count': sum(is_debt(v) for v in bucket['values'])} for name, bucket in sorted(buckets.items())]
    return report_response(request, rows, 'statistics')


@api_access(UserRole.DEANS_OFFICE)
def report_quality_api(request):
    groups = Group.objects.prefetch_related('students').order_by('name')
    if request.GET.get('group_id'):
        groups = groups.filter(pk=request.GET['group_id'])
    teachings = all_teachings()
    rows = []
    for group in groups:
        students = list(group.students.all())
        good = 0
        current_teachings = [t for t in teachings if t.group_id == group.pk]
        for student in students:
            values = [result_for_student(student, t)[0] for t in current_teachings]
            numeric = [v for v in values if isinstance(v, (int, float))]
            if numeric and all(v >= 4 for v in numeric) and all(v is not None and not is_debt(v) for v in values):
                good += 1
        rows.append({'group': group.name, 'students': len(students), 'good': good,
                     'quality_percent': round(100 * good / len(students), 1) if students else 0})
    return report_response(request, rows, 'quality')
