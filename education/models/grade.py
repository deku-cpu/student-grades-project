from django.db import models

from education.choices import GradeStatus

class Grade(models.Model):
    student = models.ForeignKey('Student', on_delete=models.PROTECT)
    assignment = models.ForeignKey('Assignment', on_delete=models.PROTECT, related_name='grades')
    value = models.CharField(max_length=10, choices=GradeStatus.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'assignment'],
                name='unique_grade_per_student_assignment',
            )
        ]

    def __str__(self):
        return f'{self.student} - {self.assignment.teaching.discipline}: {self.value}'