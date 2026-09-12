from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
from education.choices import EducationForm, Gender, StudentStatus

class Student(models.Model):
    # Студенты: ФИО, дата рождения, пол, контактные данные, группа, форма обучения (бюджет/контракт), дата поступления, статус (учится/академический отпуск/отчислен).

    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(validators=[MinValueValidator(date(1900, 1, 1)), MaxValueValidator(date.today())])
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.MALE)
    email = models.EmailField()
    phone_number = models.CharField(max_length=12)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    education_form = models.CharField(max_length=10, choices=EducationForm.choices)
    admission_date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=StudentStatus.choices, default=StudentStatus.STUDYING)

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'