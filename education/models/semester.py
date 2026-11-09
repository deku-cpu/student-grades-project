from django.db import models
from education.choices import SemesterNumber

class Semester(models.Model):
    start_year = models.PositiveSmallIntegerField()
    number = models.PositiveSmallIntegerField(choices=SemesterNumber.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['start_year', 'number'],
                name='unique_semester',
            )
        ]

    def __str__(self):
        return f'{self.start_year}/{self.start_year + 1}, семестр {self.number}'