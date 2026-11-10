from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Q

from .choices import ControlForm, GradeType
from .models import Teaching


def weighted_average(grades, assignments):
    total = Decimal('0')
    weights = Decimal('0')
    for assignment in assignments:
        value = grades.get(assignment.id)
        if str(value) in ('2', '3', '4', '5'):
            weight = Decimal(str(assignment.weight))
            total += Decimal(str(value)) * weight
            weights += weight
    if not weights:
        return None
    return float((total / weights).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def final_grade(grades, assignments, control_form):
    assignments = list(assignments)
    if control_form == ControlForm.CREDIT:
        final_values = [grades.get(a.id) for a in assignments if a.grade_type == GradeType.FINAL]
        # Зачёт определяется итоговыми работами; до них показываем промежуточный результат.
        values = [v for v in final_values if v is not None]
        if not values:
            values = [grades[a.id] for a in assignments if a.id in grades]
        if not values:
            return None
        return 'fail' if any(v in ('fail', '2') for v in values) else 'pass'
    average = weighted_average(grades, assignments)
    if average is None:
        return None
    return int(Decimal(str(average)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def mean_grade(values):
    numbers = [v for v in values if isinstance(v, (int, float))]
    return round(sum(numbers) / len(numbers), 2) if numbers else None


def is_debt(value):
    return value == 'fail' or isinstance(value, (int, float)) and value < 3


def grade_label(value):
    if value in ('2', '3', '4', '5'):
        return int(value)
    return {'pass': 'Зачёт', 'fail': 'Незачёт', None: '—'}.get(value, value)


def teachings_for_student(student):
    # Старые оценки сохраняются в ведомости после перевода в другую группу.
    condition = Q(assignments__grades__student=student)
    if student.group_id:
        condition |= Q(group_id=student.group_id)
    return Teaching.objects.filter(condition).distinct().select_related(
        'group', 'discipline', 'teacher', 'semester'
    ).prefetch_related('assignments__grades').order_by('semester__start_year', 'semester__number', 'discipline__name')


def result_for_student(student, teaching):
    assignments = list(teaching.assignments.all())
    grades = {grade.assignment_id: grade.value for assignment in assignments
              for grade in assignment.grades.all() if grade.student_id == student.pk}
    return final_grade(grades, assignments, teaching.discipline.control_form), grades, assignments
