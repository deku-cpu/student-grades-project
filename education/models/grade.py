from django.db import models

from education.choices import GradeStatus
from education.choices import ControlForm, GradeType
from django.core.exceptions import ValidationError

class Grade(models.Model):
    student = models.ForeignKey('Student', on_delete=models.PROTECT)
    assignment = models.ForeignKey('Assignment', on_delete=models.PROTECT, related_name='grades')
    value = models.CharField(max_length=10, choices=GradeStatus.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(value__in=GradeStatus.values), name='valid_grade_value'),
            models.UniqueConstraint(
                fields=['student', 'assignment'],
                name='unique_grade_per_student_assignment',
            )
        ]

    def clean(self):
        super().clean()
        if not self.student_id or not self.assignment_id:
            return
        teaching = self.assignment.teaching
        if self.student.group_id != teaching.group_id and not Grade.objects.filter(pk=self.pk, student_id=self.student_id, assignment_id=self.assignment_id).exists():
            raise ValidationError('Студент не состоит в группе этого журнала')
        if teaching.discipline.control_form == ControlForm.CREDIT:
            if self.assignment.grade_type == GradeType.FINAL and self.value not in ('pass', 'fail'):
                raise ValidationError('Для итогового зачёта выберите зачёт или незачёт')
        elif self.value in ('pass', 'fail'):
            raise ValidationError('По этой дисциплине требуется оценка от 2 до 5')

    def __str__(self):
        return f'{self.student} - {self.assignment.teaching.discipline}: {self.value}'
