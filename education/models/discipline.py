from django.db import models

from education.choices import ControlForm

class Discipline(models.Model):
    # Дисциплины: Название, краткое описание, количество часов (лекции/практики/лабораторные), форма контроля (экзамен/зачет/курсовая).

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    hours_lecture = models.PositiveSmallIntegerField(default=0)
    hours_practice = models.PositiveSmallIntegerField(default=0)
    hours_lab = models.PositiveSmallIntegerField(default=0)
    control_form = models.CharField(max_length=15, choices=ControlForm.choices)

    def __str__(self):
        return self.name