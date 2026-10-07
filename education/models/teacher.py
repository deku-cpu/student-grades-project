from django.db import models
from education.choices import PositionStatus, AcademicDegreeStatus

class Teacher(models.Model):
    # Преподаватели: ФИО, кафедра, должность, ученая степень, контактные данные.

    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    department = models.ForeignKey('Department', on_delete=models.PROTECT, related_name='teachers')
    position = models.CharField(max_length=100, choices=PositionStatus.choices)
    academic_degree = models.CharField(max_length=30, choices=AcademicDegreeStatus.choices)
    email = models.EmailField()
    phone_number = models.CharField(max_length=12)
    user = models.OneToOneField('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher_profile')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'
