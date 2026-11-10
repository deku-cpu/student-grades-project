from django.db import models
from django.core.exceptions import ValidationError


class Teaching(models.Model):
    # Группа, кто ведет, что ведет, когда ведет
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

    def clean(self):
        super().clean()
        if self.pk and self.assignments.filter(grades__isnull=False).exists():
            previous = Teaching.objects.get(pk=self.pk)
            if any(getattr(previous, field) != getattr(self, field) for field in ('group_id', 'discipline_id', 'semester_id')):
                raise ValidationError('В журнале уже есть оценки. Группу, дисциплину и семестр менять нельзя')

    def __str__(self):
        return f'{self.group} - {self.discipline} ({self.semester})'
