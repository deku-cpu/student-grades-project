from django.db import models
from education.choices import GradeStatus

class Grade(models.Model):
    student = models.ForeignKey('Student', on_delete=models.PROTECT)
    teaching = models.ForeignKey('Teaching', on_delete=models.PROTECT, related_name='grades')
    value = models.CharField(max_length=10, choices=GradeStatus.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'teaching'],
                name='unique_grade_per_student_teaching',
            )
        ]

    def __str__(self):
        return f'{self.student} - {self.teaching.discipline}: {self.value}'