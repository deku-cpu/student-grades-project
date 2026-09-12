from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Group(models.Model):
    # Группы: Название, специальность, курс, форма обучения, год набора, куратор.

    name = models.CharField(max_length=100, unique=True)
    specialty = models.ForeignKey('Specialty', on_delete=models.PROTECT, related_name='groups')
    course = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    admission_year = models.PositiveSmallIntegerField(validators=[MinValueValidator(2000)])
    curator = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='curated_groups')

    def __str__(self):
        return self.name
