from django.db import models


class Teaching(models.Model):
    group = models.ForeignKey('Group', on_delete=models.PROTECT, related_name='teachings')
    discipline = models.ForeignKey('Discipline', on_delete=models.PROTECT, related_name='teachings')
    semester = models.ForeignKey('Semester', on_delete=models.PROTECT, related_name='teachings')
    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='teachings')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'discipline', 'semester', 'teacher'],
                name='unique_teaching_per_semester',
            )
        ]

    def __str__(self):
        return f'{self.group} - {self.discipline} ({self.semester})'