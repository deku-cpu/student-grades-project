import io

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from .access import api_access, can_manage, check_teaching, error_response, read_json, save_checked, user_role
from .choices import UserRole
from .grading import final_grade, result_for_student, teachings_for_student, weighted_average
from .models import Assignment, AuditLog, Department, Discipline, Grade, Group, Semester, Specialty, Student, Teacher, Teaching


MANAGERS = (UserRole.DEANS_OFFICE,)


def response(data):
    return JsonResponse(data, safe=isinstance(data, dict), json_dumps_params={'ensure_ascii': False})


def teacher_name(teacher):
    initials = ''.join(name[:1] + '.' for name in (teacher.first_name, teacher.middle_name) if name)
    return f'{teacher.last_name} {initials}'.strip()


def update_fields(obj, data, fields):
    for field in fields:
        if field in data:
            setattr(obj, field, data[field])
    return obj


@api_access(methods=('POST',))
def login_api(request):
    data = read_json(request)
    username, password = data.get('username'), data.get('password')
    if not isinstance(username, str) or not isinstance(password, str):
        return error_response('Введите логин и пароль')
    user = authenticate(request=request, username=username, password=password)
    if not user:
        return error_response('Неверный логин или пароль', 401)
    if not user_role(user):
        return error_response('Пользователю не назначена роль. Обратитесь к администратору', 403)
    login(request, user)
    request.session.set_expiry(14 * 24 * 60 * 60 if data.get('remember') is True else 0)
    return response({'username': user.username, 'role': user_role(user)})


@api_access(*UserRole.values)
def me_api(request):
    student = getattr(request.user, 'student_profile', None)
    return response({'username': request.user.username, 'role': user_role(request.user),
                     'student_id': student.pk if student else None})


@api_access(*UserRole.values, methods=('POST',))
def logout_api(request):
    logout(request)
    return response({'ok': True})


@api_access(*MANAGERS, methods=('GET', 'POST'))
def groups_api(request):
    if request.method == 'POST':
        group = fill_group(Group(), read_json(request))
        save_checked(group)
        return response({'ok': True, 'id': group.pk})
    groups = Group.objects.select_related('specialty', 'curator').annotate(students_count=Count('students', distinct=True))
    for param, field in [('search', 'name__icontains'), ('course', 'course'), ('form', 'mode_of_study'), ('specialty', 'specialty_id')]:
        if request.GET.get(param):
            groups = groups.filter(**{field: request.GET[param]})
    return response([{'id': g.pk, 'name': g.name, 'yearOfStudy': g.course,
                      'specialty_id': g.specialty_id, 'specialty': g.specialty.name,
                      'form': g.mode_of_study, 'form_label': g.get_mode_of_study_display(),
                      'admissionYear': g.admission_year, 'students': g.students_count,
                      'curator_id': g.curator_id or '', 'curator': str(g.curator) if g.curator else '—'}
                     for g in groups.order_by('name')])


def fill_group(group, data):
    mapping = {'name': 'name', 'course': 'course', 'form': 'mode_of_study',
               'admissionYear': 'admission_year', 'specialty': 'specialty_id', 'curator_id': 'curator_id'}
    for source, target in mapping.items():
        if source in data:
            setattr(group, target, (data[source] or None) if target == 'curator_id' else data[source])
    return group


@api_access(*MANAGERS, methods=('PUT', 'DELETE'))
def group_detail_api(request, group_id):
    group = Group.objects.get(pk=group_id)
    if request.method == 'DELETE':
        group.delete()
    else:
        save_checked(fill_group(group, read_json(request)))
    return response({'ok': True})


REFERENCE_MODELS = {'specialities': (Specialty, ('code', 'name')),
                    'departments': (Department, ('name',)),
                    'semesters': (Semester, ('start_year', 'number'))}


@api_access(*MANAGERS, methods=('GET', 'POST', 'PUT', 'DELETE'))
def reference_api(request, reference, object_id=None):
    if reference not in REFERENCE_MODELS:
        return error_response('Справочник не найден', 404)
    model, fields = REFERENCE_MODELS[reference]
    if object_id is None:
        if request.method == 'GET':
            objects = model.objects.all().order_by(*fields)
            search = request.GET.get('search', '').strip()
            data = [dict(id=obj.pk, label=str(obj), **{f: getattr(obj, f) for f in fields}) for obj in objects]
            return response([item for item in data if search.lower() in item['label'].lower()])
        if request.method != 'POST':
            return error_response('Метод не поддерживается', 405)
        obj = save_checked(update_fields(model(), read_json(request), fields))
        return response({'ok': True, 'id': obj.pk})
    obj = model.objects.get(pk=object_id)
    if request.method == 'DELETE':
        obj.delete()
    elif request.method == 'PUT':
        save_checked(update_fields(obj, read_json(request), fields))
    else:
        return error_response('Метод не поддерживается', 405)
    return response({'ok': True})


@api_access(*MANAGERS)
def speciality_api(request):
    return response(list(Specialty.objects.order_by('code').values('id', 'code', 'name')))


STUDENT_FIELDS = ('last_name', 'first_name', 'middle_name', 'date_of_birth', 'gender', 'email',
                  'phone_number', 'education_form', 'admission_date', 'status')
TEACHER_FIELDS = ('last_name', 'first_name', 'middle_name', 'position', 'academic_degree', 'email', 'phone_number')
DISCIPLINE_FIELDS = ('name', 'description', 'hours_lecture', 'hours_practice', 'hours_lab', 'control_form')


def student_data(student):
    data = {field: getattr(student, field) for field in STUDENT_FIELDS}
    data.update(id=student.pk, full_name=str(student), group_id=student.group_id or '',
                group_name=student.group.name if student.group else 'Нет',
                education_form_label=student.get_education_form_display(),
                status_label=student.get_status_display(), gender_label=student.get_gender_display())
    return data


@api_access(*MANAGERS, methods=('GET', 'POST'))
def students_api(request):
    if request.method == 'POST':
        data = read_json(request)
        student = update_fields(Student(), data, STUDENT_FIELDS)
        student.group_id = data.get('group_id') or None
        save_checked(student)
        return response({'ok': True, 'id': student.pk})
    students = Student.objects.select_related('group').all()
    search = request.GET.get('search')
    if search:
        students = students.filter(Q(last_name__icontains=search) | Q(first_name__icontains=search) | Q(middle_name__icontains=search))
    for param, field in [('group', 'group_id'), ('form', 'education_form'), ('status', 'status')]:
        if request.GET.get(param):
            students = students.filter(**{field: request.GET[param]})
    return response([student_data(s) for s in students.order_by('last_name', 'first_name', 'id')])


@api_access(*MANAGERS, methods=('GET', 'PUT', 'DELETE'))
def student_detail_api(request, student_id):
    student = Student.objects.select_related('group').get(pk=student_id)
    if request.method == 'GET':
        return response(student_data(student))
    if request.method == 'DELETE':
        if Grade.objects.filter(student=student).exists():
            return error_response('У студента есть оценки, поэтому удаление запрещено. Для отчисления выберите в карточке редактирования статус «Отчислен» — история успеваемости сохранится.', 409)
        student.delete()
    else:
        data = read_json(request)
        update_fields(student, data, STUDENT_FIELDS)
        if 'group_id' in data:
            student.group_id = data['group_id'] or None
        save_checked(student)
    return response({'ok': True})


@api_access(*MANAGERS, methods=('GET', 'POST'))
def teachers_api(request):
    if request.method == 'POST':
        data = read_json(request)
        teacher = update_fields(Teacher(), data, TEACHER_FIELDS)
        teacher.department_id = data.get('department_id')
        save_checked(teacher)
        return response({'ok': True, 'id': teacher.pk})
    teachers = Teacher.objects.select_related('department').all()
    search = request.GET.get('search')
    if search:
        teachers = teachers.filter(Q(last_name__icontains=search) | Q(first_name__icontains=search) | Q(middle_name__icontains=search))
    for param, field in [('department', 'department_id'), ('position', 'position')]:
        if request.GET.get(param):
            teachers = teachers.filter(**{field: request.GET[param]})
    data = []
    for teacher in teachers.order_by('last_name', 'first_name', 'id'):
        item = {field: getattr(teacher, field) for field in TEACHER_FIELDS}
        item.update(id=teacher.pk, full_name=str(teacher), department_id=teacher.department_id,
                    department_name=teacher.department.name, position_label=teacher.get_position_display(),
                    academic_degree_label=teacher.get_academic_degree_display() or 'Нет степени')
        data.append(item)
    return response(data)


@api_access(*MANAGERS, methods=('PUT', 'DELETE'))
def teacher_detail_api(request, teacher_id):
    teacher = Teacher.objects.get(pk=teacher_id)
    if request.method == 'DELETE':
        teacher.delete()
    else:
        data = read_json(request)
        update_fields(teacher, data, TEACHER_FIELDS)
        if 'department_id' in data:
            teacher.department_id = data['department_id']
        save_checked(teacher)
    return response({'ok': True})


@api_access(*MANAGERS, methods=('GET', 'POST'))
def disciplines_api(request):
    if request.method == 'POST':
        discipline = save_checked(update_fields(Discipline(), read_json(request), DISCIPLINE_FIELDS))
        return response({'ok': True, 'id': discipline.pk})
    disciplines = Discipline.objects.all()
    if request.GET.get('search'):
        disciplines = disciplines.filter(name__icontains=request.GET['search'])
    if request.GET.get('control_form'):
        disciplines = disciplines.filter(control_form=request.GET['control_form'])
    return response([dict(id=d.pk, control_form_label=d.get_control_form_display(),
                          **{field: getattr(d, field) for field in DISCIPLINE_FIELDS})
                     for d in disciplines.order_by('name')])


@api_access(*MANAGERS, methods=('PUT', 'DELETE'))
def discipline_detail_api(request, discipline_id):
    discipline = Discipline.objects.get(pk=discipline_id)
    if request.method == 'DELETE':
        discipline.delete()
    else:
        save_checked(update_fields(discipline, read_json(request), DISCIPLINE_FIELDS))
    return response({'ok': True})


@api_access(UserRole.TEACHER, UserRole.DEANS_OFFICE, methods=('GET', 'POST'))
def teachings_api(request):
    if request.method == 'POST':
        if not can_manage(request.user):
            raise PermissionDenied('Назначать дисциплины может только деканат')
        teaching = save_checked(update_fields(Teaching(), read_json(request), ('group_id', 'discipline_id', 'teacher_id', 'semester_id')))
        return response({'ok': True, 'id': teaching.pk})
    teachings = Teaching.objects.select_related('group', 'discipline', 'teacher', 'semester').all()
    if not can_manage(request.user):
        teachings = teachings.filter(teacher__user=request.user)
    if request.GET.get('search'):
        teachings = teachings.filter(Q(group__name__icontains=request.GET['search']) | Q(discipline__name__icontains=request.GET['search']))
    return response([{'id': t.pk, 'group_id': t.group_id, 'group_name': t.group.name,
                      'discipline_id': t.discipline_id, 'discipline_name': t.discipline.name,
                      'teacher_id': t.teacher_id, 'teacher_name': teacher_name(t.teacher),
                      'semester_id': t.semester_id, 'semester_name': str(t.semester)}
                     for t in teachings.order_by('group__name', 'discipline__name')])


@api_access(*MANAGERS, methods=('PUT', 'DELETE'))
def teaching_detail_api(request, teaching_id):
    teaching = Teaching.objects.get(pk=teaching_id)
    if request.method == 'DELETE':
        teaching.delete()
    else:
        save_checked(update_fields(teaching, read_json(request), ('group_id', 'discipline_id', 'teacher_id', 'semester_id')))
    return response({'ok': True})


@api_access(UserRole.TEACHER, UserRole.DEANS_OFFICE)
def teacher_disciplines_api(request):
    teachings = Teaching.objects.select_related('group', 'discipline', 'teacher').all()
    if not can_manage(request.user):
        teachings = teachings.filter(teacher__user=request.user)
    for param, field in [('search_discipline', 'discipline__name__icontains'), ('search_group', 'group__name__icontains'), ('course', 'group__course')]:
        if request.GET.get(param):
            teachings = teachings.filter(**{field: request.GET[param]})
    return response([{'id': t.pk, 'discipline': t.discipline.name, 'group': t.group.name, 'course': t.group.course}
                     for t in teachings.order_by('group__name', 'discipline__name')])


def fill_assignment(assignment, data):
    update_fields(assignment, data, ('title', 'grade_type', 'weight', 'order'))
    if 'date' in data:
        assignment.date = data['date'] or None
    return assignment


@api_access(UserRole.TEACHER, UserRole.DEANS_OFFICE, methods=('GET', 'POST'))
def assignments_api(request, teaching_id):
    teaching = Teaching.objects.select_related('teacher').get(pk=teaching_id)
    check_teaching(request.user, teaching)
    if request.method == 'POST':
        assignment = save_checked(fill_assignment(Assignment(teaching=teaching), read_json(request)))
        return response({'ok': True, 'id': assignment.pk})
    return response([{'id': a.pk, 'title': a.title, 'grade_type': a.grade_type,
                      'grade_type_label': a.get_grade_type_display(), 'weight': a.weight,
                      'order': a.order, 'date': a.date.isoformat() if a.date else ''}
                     for a in teaching.assignments.all()])


@api_access(UserRole.TEACHER, UserRole.DEANS_OFFICE, methods=('PUT', 'DELETE'))
def assignment_detail_api(request, assignment_id):
    assignment = Assignment.objects.select_related('teaching__teacher').get(pk=assignment_id)
    check_teaching(request.user, assignment.teaching)
    if request.method == 'DELETE':
        assignment.delete()
    else:
        save_checked(fill_assignment(assignment, read_json(request)))
    return response({'ok': True})


@api_access(UserRole.TEACHER, UserRole.DEANS_OFFICE)
def journal_api(request, teaching_id):
    teaching = Teaching.objects.select_related('group', 'discipline', 'teacher').prefetch_related('assignments__grades').get(pk=teaching_id)
    check_teaching(request.user, teaching)
    students = Student.objects.filter(Q(group=teaching.group) | Q(grade__assignment__teaching=teaching)).distinct().order_by('last_name', 'first_name')
    assignments = list(teaching.assignments.all())
    data = []
    for student in students:
        final, grades, unused = result_for_student(student, teaching)
        data.append({'id': student.pk, 'full_name': str(student), 'grades': grades,
                     'final_grade': final, 'weighted_average': weighted_average(grades, assignments),
                     'transferred': student.group_id != teaching.group_id})
    return response({'group_name': teaching.group.name, 'discipline_name': teaching.discipline.name,
                     'control_form': teaching.discipline.control_form,
                     'assignments': [{'id': a.pk, 'title': a.title, 'weight': a.weight, 'grade_type': a.grade_type} for a in assignments],
                     'students': data})


@api_access(UserRole.TEACHER, UserRole.DEANS_OFFICE, methods=('POST',))
def grades_api(request):
    data = read_json(request)
    assignment = Assignment.objects.select_related('teaching__teacher', 'teaching__discipline').get(pk=data['assignment_id'])
    check_teaching(request.user, assignment.teaching)
    student = Student.objects.get(pk=data['student_id'])
    value = data.get('value')
    if not isinstance(value, str):
        raise ValidationError('Оценка должна быть строкой: 2, 3, 4, 5, pass или fail')
    grade = Grade.objects.filter(student=student, assignment=assignment).first()
    if not grade and student.group_id != assignment.teaching.group_id:
        raise ValidationError('Студент не состоит в группе этого журнала')
    if value == '':
        if grade:
            grade.delete()
    else:
        grade = grade or Grade(student=student, assignment=assignment)
        grade.value = value
        save_checked(grade)
    assignments = list(assignment.teaching.assignments.all())
    grades = dict(Grade.objects.filter(student=student, assignment__in=assignments).values_list('assignment_id', 'value'))
    return response({'ok': True, 'message': 'Оценка удалена' if value == '' else 'Оценка сохранена',
                     'final_grade': final_grade(grades, assignments, assignment.teaching.discipline.control_form),
                     'weighted_average': weighted_average(grades, assignments)})


@api_access(UserRole.STUDENT)
def student_diary_api(request):
    student = getattr(request.user, 'student_profile', None)
    if not student:
        return error_response('Учётная запись не связана со студентом', 404)
    data = []
    for teaching in teachings_for_student(student):
        final, grades, assignments = result_for_student(student, teaching)
        data.append({'teaching_id': teaching.pk, 'discipline': teaching.discipline.name,
                     'teacher': teacher_name(teaching.teacher), 'semester': str(teaching.semester),
                     'group': teaching.group.name, 'assignments': [{'id': a.pk, 'title': a.title} for a in assignments],
                     'grades': grades, 'final_grade': final, 'weighted_average': weighted_average(grades, assignments)})
    return response(data)


@api_access(UserRole.ADMIN)
def audit_api(request):
    logs = AuditLog.objects.select_related('user').all()
    if request.GET.get('search'):
        logs = logs.filter(Q(user__username__icontains=request.GET['search']) | Q(path__icontains=request.GET['search']) | Q(action__icontains=request.GET['search']))
    return response([{'id': log.pk, 'user': log.user.username if log.user else 'Удалённый пользователь',
                      'action': log.action, 'path': log.path, 'created_at': timezone.localtime(log.created_at).strftime('%d.%m.%Y %H:%M:%S')}
                     for log in logs[:500]])


@api_access(UserRole.ADMIN, methods=('POST',))
def backup_api(request):
    from .backups import write_backup
    # Копия содержит данные и учётные записи; доступна только администратору.
    output = io.StringIO()
    write_backup(output)
    result = HttpResponse(output.getvalue(), content_type='application/json; charset=utf-8')
    filename = timezone.localtime().strftime('grades-backup-%Y%m%d-%H%M%S.json')
    result['Content-Disposition'] = f'attachment; filename="{filename}"'
    return result
