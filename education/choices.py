from django.db import models


class Gender(models.TextChoices):
    MALE = 'M', 'Мужской'
    FEMALE = 'F', 'Женский'

class EducationForm(models.TextChoices):
    BUDGET = 'budget', 'Бюджет'
    CONTRACT = 'contract', 'Контракт'

class ControlForm(models.TextChoices):
    EXAM = 'exam', 'Экзамен'
    CREDIT = 'credit', 'Зачет'
    COURSE_WORK = 'course_work', 'Курсовая'

class StudentStatus(models.TextChoices):
    STUDYING = 'studying', 'Учится'
    ACADEMIC_LEAVE = 'academic_leave', 'Академический отпуск'
    EXPELLED = 'expelled', 'Отчислен'

class PositionStatus(models.TextChoices):
    LABORATORY_ASSISTANT = 'laboratory_assistant', 'Лаборант'
    ASSISTANT = 'assistant', 'Ассистент'
    SENIOR_LECTURER = 'senior_lecturer', 'Старший преподаватель'
    ASSOCIATE_PROFESSOR = 'associate_professor', 'Доцент'
    PROFESSOR = 'professor', 'Профессор'

class AcademicDegreeStatus(models.TextChoices):
    CANDIDATE_OF_SCIENCES = 'candidate_of_sciences', 'Кандидат Наук'
    DOCTOR_OF_SCIENCE = 'doctor_of_science', 'Доктор Наук'

class SemesterNumber(models.IntegerChoices):
    FIRST = 1, '1 семестр'
    SECOND = 2, '2 семестр'

class GradeStatus(models.TextChoices):
    TWO = '2', '2 (неудовлетворительно)'
    THREE = '3', '3 (удовлетворительно)'
    FOUR = '4', '4 (хорошо)'
    FIVE = '5', '5 (отлично)'
    PASS = 'pass', 'Зачет'
    FAIL = 'fail', 'Незачет'

class GroupStatus(models.TextChoices):
    FULL_TIME = 'full-time', 'Очная'
    PART_TIME = 'part-time', 'Заочная'
    HYBRID_PROGRAM = 'hybrid-program', 'Очно-заочная'

class GradeType(models.TextChoices):
    INTERMEDIATE = 'intermediate', 'Промежуточная оценка'
    FINAL = 'final', 'Итоговая оценка'

class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Администратор'
    DEANS_OFFICE = 'deans_office', 'Деканат'
    TEACHER = 'teacher', 'Преподаватель'
    STUDENT = 'student', 'Студент'