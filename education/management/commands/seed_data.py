import random
from datetime import date

from django.core.management.base import BaseCommand

from education.models import (
    Specialty, Department, Semester, Teacher, Group,
    Student, Discipline, Teaching, Grade,
)
from education.choices import (
    PositionStatus, AcademicDegreeStatus, Gender,
    EducationForm, StudentStatus, ControlForm, GradeStatus,
)


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными'

    def handle(self, *args, **options):
        self.create_specialties()
        self.create_departments()
        self.create_semesters()
        self.create_teachers()
        self.create_groups()
        self.create_students()
        self.create_disciplines()
        self.create_teaching()
        self.create_grades()
        self.stdout.write(self.style.SUCCESS('Готово!'))

    def create_specialties(self):
        data = [
            ('09.03.01', 'Информатика и вычислительная техника'),
            ('09.03.02', 'Информационные системы и технологии'),
            ('09.03.03', 'Прикладная информатика'),
            ('09.03.04', 'Программная инженерия'),
        ]

        for code, name in data:
            obj, created = Specialty.objects.get_or_create(code=code, defaults={'name': name})
            self.stdout.write(f'Специальность {obj}: {"создана" if created else "уже есть"}')

    def create_departments(self):
        names = [
            'Кафедра информатики',
            'Кафедра высшей математики',
            'Кафедра программной инженерии',
        ]

        for name in names:
            obj, created = Department.objects.get_or_create(name=name)
            self.stdout.write(f'Кафедра {obj}: {"создана" if created else "уже есть"}')

    def create_semesters(self):
        for year in (2024, 2025):
            for number in (1, 2):
                obj, created = Semester.objects.get_or_create(start_year=year, number=number)
                self.stdout.write(f'Семестр {obj}: {"создан" if created else "уже есть"}')

    def create_teachers(self):
        departments = {department.name: department for department in Department.objects.all()}

        data = [
            ('Кузнецов', 'Андрей', 'Павлович', 'Кафедра информатики',
             PositionStatus.PROFESSOR, AcademicDegreeStatus.DOCTOR_OF_SCIENCE,
             'kuznetsov@univ.ru', '+79001110001'),
            ('Смирнова', 'Елена', 'Викторовна', 'Кафедра информатики',
             PositionStatus.ASSOCIATE_PROFESSOR, AcademicDegreeStatus.CANDIDATE_OF_SCIENCES,
             'smirnova@univ.ru', '+79001110002'),
            ('Попов', 'Дмитрий', 'Сергеевич', 'Кафедра информатики',
             PositionStatus.ASSOCIATE_PROFESSOR, AcademicDegreeStatus.CANDIDATE_OF_SCIENCES,
             'popov@univ.ru', '+79001110003'),
            ('Васильева', 'Ольга', 'Николаевна', 'Кафедра информатики',
             PositionStatus.SENIOR_LECTURER, AcademicDegreeStatus.CANDIDATE_OF_SCIENCES,
             'vasileva@univ.ru', '+79001110004'),
            ('Морозов', 'Игорь', 'Алексеевич', 'Кафедра высшей математики',
             PositionStatus.PROFESSOR, AcademicDegreeStatus.DOCTOR_OF_SCIENCE,
             'morozov@univ.ru', '+79001110005'),
            ('Новикова', 'Татьяна', 'Михайловна', 'Кафедра высшей математики',
             PositionStatus.ASSOCIATE_PROFESSOR, AcademicDegreeStatus.CANDIDATE_OF_SCIENCES,
             'novikova@univ.ru', '+79001110006'),
            ('Фёдоров', 'Максим', 'Олегович', 'Кафедра высшей математики',
             PositionStatus.ASSISTANT, AcademicDegreeStatus.CANDIDATE_OF_SCIENCES,
             'fedorov@univ.ru', '+79001110007'),
            ('Соколов', 'Роман', 'Владимирович', 'Кафедра программной инженерии',
             PositionStatus.ASSOCIATE_PROFESSOR, AcademicDegreeStatus.CANDIDATE_OF_SCIENCES,
             'sokolov@univ.ru', '+79001110008'),
            ('Лебедева', 'Наталья', 'Андреевна', 'Кафедра программной инженерии',
             PositionStatus.SENIOR_LECTURER, AcademicDegreeStatus.CANDIDATE_OF_SCIENCES,
             'lebedeva@univ.ru', '+79001110009'),
            ('Егоров', 'Павел', 'Игоревич', 'Кафедра программной инженерии',
             PositionStatus.ASSOCIATE_PROFESSOR, AcademicDegreeStatus.DOCTOR_OF_SCIENCE,
             'egorov@univ.ru', '+79001110010'),
            ('Орлова', 'Анна', 'Дмитриевна', 'Кафедра информатики',
             PositionStatus.LABORATORY_ASSISTANT, AcademicDegreeStatus.CANDIDATE_OF_SCIENCES,
             'orlova@univ.ru', '+79001110011'),
            ('Зайцев', 'Илья', 'Романович', 'Кафедра высшей математики',
             PositionStatus.ASSISTANT, AcademicDegreeStatus.CANDIDATE_OF_SCIENCES,
             'zaytsev@univ.ru', '+79001110012'),
        ]

        for last_name, first_name, middle_name, department_name, position, academic_degree, email, phone in data:
            department = departments[department_name]
            obj, created = Teacher.objects.get_or_create(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                defaults={
                    'department': department,
                    'position': position,
                    'academic_degree': academic_degree,
                    'email': email,
                    'phone_number': phone,
                },
            )
            self.stdout.write(f'Преподаватель {obj}: {"создан" if created else "уже есть"}')

    def create_groups(self):
        specialties = {specialty.code: specialty for specialty in Specialty.objects.all()}
        teachers = {teacher.last_name: teacher for teacher in Teacher.objects.all()}

        data = [
            ('ИВТ-24', '09.03.01', 3, 2024, 'Кузнецов'),
            ('ИС-25', '09.03.02', 2, 2025, 'Смирнова'),
            ('ПИ-25', '09.03.03', 2, 2025, 'Новикова'),
            ('ПИ-24', '09.03.04', 3, 2024, 'Соколов'),
            ('ИВТ-25', '09.03.01', 2, 2025, None),
        ]

        for name, specialty_code, course, admission_year, curator_name in data:
            specialty = specialties[specialty_code]
            curator = teachers[curator_name] if curator_name else None

            obj, created = Group.objects.get_or_create(
                name=name,
                defaults={
                    'specialty': specialty,
                    'course': course,
                    'admission_year': admission_year,
                    'curator': curator,
                },
            )
            self.stdout.write(f'Группа {obj}: {"создана" if created else "уже есть"}')

    def create_students(self):
        groups = {group.name: group for group in Group.objects.all()}

        data = [
            # ИВТ-24
            ('Иванов', 'Иван', 'Иванович', date(2006, 3, 14), Gender.MALE,
             'ivanov@student.ru', '+79101110001', 'ИВТ-24', EducationForm.BUDGET,
             date(2024, 9, 1), StudentStatus.STUDYING),
            ('Петрова', 'Мария', 'Сергеевна', date(2006, 7, 22), Gender.FEMALE,
             'petrova@student.ru', '+79101110002', 'ИВТ-24', EducationForm.CONTRACT,
             date(2024, 9, 1), StudentStatus.STUDYING),
            ('Сидоров', 'Алексей', 'Дмитриевич', date(2005, 11, 5), Gender.MALE,
             'sidorov@student.ru', '+79101110003', 'ИВТ-24', EducationForm.BUDGET,
             date(2024, 9, 1), StudentStatus.ACADEMIC_LEAVE),
            ('Кузьмина', 'Дарья', 'Олеговна', date(2006, 1, 30), Gender.FEMALE,
             'kuzmina@student.ru', '+79101110004', 'ИВТ-24', EducationForm.BUDGET,
             date(2024, 9, 1), StudentStatus.STUDYING),

            # ИС-25
            ('Волков', 'Никита', 'Андреевич', date(2007, 4, 18), Gender.MALE,
             'volkov@student.ru', '+79101110005', 'ИС-25', EducationForm.CONTRACT,
             date(2025, 9, 1), StudentStatus.STUDYING),
            ('Соловьёва', 'Анастасия', 'Игоревна', date(2007, 9, 2), Gender.FEMALE,
             'soloveva@student.ru', '+79101110006', 'ИС-25', EducationForm.BUDGET,
             date(2025, 9, 1), StudentStatus.STUDYING),
            ('Тарасов', 'Егор', 'Максимович', date(2006, 12, 25), Gender.MALE,
             'tarasov@student.ru', '+79101110007', 'ИС-25', EducationForm.BUDGET,
             date(2025, 9, 1), StudentStatus.STUDYING),
            ('Белова', 'Виктория', 'Романовна', date(2007, 6, 11), Gender.FEMALE,
             'belova@student.ru', '+79101110008', 'ИС-25', EducationForm.CONTRACT,
             date(2025, 9, 1), StudentStatus.EXPELLED),

            # ПИ-25
            ('Комаров', 'Артём', 'Вячеславович', date(2007, 2, 9), Gender.MALE,
             'komarov@student.ru', '+79101110009', 'ПИ-25', EducationForm.BUDGET,
             date(2025, 9, 1), StudentStatus.STUDYING),
            ('Орлова', 'Полина', 'Денисовна', date(2007, 8, 17), Gender.FEMALE,
             'orlova.p@student.ru', '+79101110010', 'ПИ-25', EducationForm.BUDGET,
             date(2025, 9, 1), StudentStatus.STUDYING),
            ('Григорьев', 'Матвей', 'Олегович', date(2006, 10, 3), Gender.MALE,
             'grigoriev@student.ru', '+79101110011', 'ПИ-25', EducationForm.CONTRACT,
             date(2025, 9, 1), StudentStatus.STUDYING),
            ('Никитина', 'Софья', 'Артёмовна', date(2007, 5, 28), Gender.FEMALE,
             'nikitina@student.ru', '+79101110012', 'ПИ-25', EducationForm.BUDGET,
             date(2025, 9, 1), StudentStatus.STUDYING),

            # ПИ-24
            ('Захаров', 'Даниил', 'Игоревич', date(2006, 3, 19), Gender.MALE,
             'zaharov@student.ru', '+79101110013', 'ПИ-24', EducationForm.BUDGET,
             date(2024, 9, 1), StudentStatus.STUDYING),
            ('Афанасьева', 'Елизавета', 'Юрьевна', date(2005, 9, 24), Gender.FEMALE,
             'afanaseva@student.ru', '+79101110014', 'ПИ-24', EducationForm.CONTRACT,
             date(2024, 9, 1), StudentStatus.STUDYING),
            ('Мельников', 'Кирилл', 'Станиславович', date(2006, 7, 7), Gender.MALE,
             'melnikov@student.ru', '+79101110015', 'ПИ-24', EducationForm.BUDGET,
             date(2024, 9, 1), StudentStatus.STUDYING),
            ('Гусева', 'Ксения', 'Алексеевна', date(2005, 12, 12), Gender.FEMALE,
             'guseva@student.ru', '+79101110016', 'ПИ-24', EducationForm.BUDGET,
             date(2024, 9, 1), StudentStatus.ACADEMIC_LEAVE),

            # ИВТ-25
            ('Панов', 'Владислав', 'Николаевич', date(2007, 1, 15), Gender.MALE,
             'panov@student.ru', '+79101110017', 'ИВТ-25', EducationForm.BUDGET,
             date(2025, 9, 1), StudentStatus.STUDYING),
            ('Ковалёва', 'Алина', 'Викторовна', date(2007, 3, 27), Gender.FEMALE,
             'kovaleva@student.ru', '+79101110018', 'ИВТ-25', EducationForm.CONTRACT,
             date(2025, 9, 1), StudentStatus.STUDYING),
            ('Фомин', 'Тимофей', 'Андреевич', date(2006, 11, 9), Gender.MALE,
             'fomin@student.ru', '+79101110019', 'ИВТ-25', EducationForm.BUDGET,
             date(2025, 9, 1), StudentStatus.STUDYING),
            ('Титова', 'Вероника', 'Павловна', date(2007, 4, 4), Gender.FEMALE,
             'titova@student.ru', '+79101110020', 'ИВТ-25', EducationForm.BUDGET,
             date(2025, 9, 1), StudentStatus.STUDYING),
        ]

        for (last_name, first_name, middle_name, date_of_birth, gender,
             email, phone, group_name, education_form, admission_date, status) in data:
            group = groups[group_name]

            obj, created = Student.objects.get_or_create(
                email=email,
                defaults={
                    'last_name': last_name,
                    'first_name': first_name,
                    'middle_name': middle_name,
                    'date_of_birth': date_of_birth,
                    'gender': gender,
                    'phone_number': phone,
                    'group': group,
                    'education_form': education_form,
                    'admission_date': admission_date,
                    'status': status,
                },
            )
            self.stdout.write(f'Студент {obj} ({email}): {"создан" if created else "уже есть"}')

    def create_disciplines(self):
        data = [
            ('Программирование', 'Основы алгоритмизации и программирования', 24, 32, 16, ControlForm.EXAM),
            ('Базы данных', 'Проектирование и работа с реляционными БД', 16, 16, 32, ControlForm.EXAM),
            ('Высшая математика', 'Математический анализ и линейная алгебра', 32, 32, 0, ControlForm.EXAM),
            ('Дискретная математика', 'Теория множеств, графы, комбинаторика', 16, 16, 0, ControlForm.CREDIT),
            ('Операционные системы', 'Устройство и администрирование ОС', 16, 16, 16, ControlForm.CREDIT),
            ('Компьютерные сети', 'Основы сетевых технологий и протоколов', 16, 16, 16, ControlForm.EXAM),
            ('Объектно-ориентированное программирование', 'Принципы ООП на примере современных языков', 16, 16, 32, ControlForm.COURSE_WORK),
            ('Web-разработка', 'Разработка веб-приложений: frontend и backend', 8, 8, 32, ControlForm.CREDIT),
            ('Алгоритмы и структуры данных', 'Основные алгоритмы и структуры данных', 16, 16, 16, ControlForm.EXAM),
            ('Проектирование информационных систем', 'Методологии анализа и проектирования ИС', 16, 8, 16, ControlForm.COURSE_WORK),
            ('Английский язык', 'Иностранный язык для технических специальностей', 0, 32, 0, ControlForm.CREDIT),
            ('Физика', 'Общий курс физики', 16, 16, 16, ControlForm.EXAM),
            ('Экономика', 'Основы экономической теории', 16, 16, 0, ControlForm.CREDIT),
            ('Информационная безопасность', 'Основы защиты информации', 16, 16, 16, ControlForm.CREDIT),
            ('Технологии программной инженерии', 'Жизненный цикл разработки ПО', 16, 8, 16, ControlForm.COURSE_WORK),
        ]

        for name, description, hours_lecture, hours_practice, hours_lab, control_form in data:
            obj, created = Discipline.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'hours_lecture': hours_lecture,
                    'hours_practice': hours_practice,
                    'hours_lab': hours_lab,
                    'control_form': control_form,
                },
            )
            self.stdout.write(f'Дисциплина {obj}: {"создана" if created else "уже есть"}')

    def create_teaching(self):
        teachers = {t.last_name: t for t in Teacher.objects.all()}
        disciplines = {d.name: d for d in Discipline.objects.all()}
        groups = {g.name: g for g in Group.objects.all()}
        semesters = {(s.start_year, s.number): s for s in Semester.objects.all()}

        data = [
            # ИВТ-24
            ('Кузнецов', 'Программирование', 'ИВТ-24', 2024, 1),
            ('Смирнова', 'Базы данных', 'ИВТ-24', 2024, 1),
            ('Морозов', 'Высшая математика', 'ИВТ-24', 2024, 1),

            # ИС-25
            ('Попов', 'Алгоритмы и структуры данных', 'ИС-25', 2025, 1),
            ('Новикова', 'Дискретная математика', 'ИС-25', 2025, 1),
            ('Васильева', 'Web-разработка', 'ИС-25', 2025, 1),
            ('Васильева', 'Английский язык', 'ИС-25', 2025, 1),

            # ПИ-25
            ('Соколов', 'Объектно-ориентированное программирование', 'ПИ-25', 2025, 1),
            ('Фёдоров', 'Физика', 'ПИ-25', 2025, 1),
            ('Лебедева', 'Технологии программной инженерии', 'ПИ-25', 2025, 1),

            # ПИ-24
            ('Егоров', 'Проектирование информационных систем', 'ПИ-24', 2024, 1),
            ('Соколов', 'Компьютерные сети', 'ПИ-24', 2024, 1),
            ('Новикова', 'Экономика', 'ПИ-24', 2024, 1),
            ('Егоров', 'Информационная безопасность', 'ПИ-24', 2024, 1),

            # ИВТ-25
            ('Смирнова', 'Операционные системы', 'ИВТ-25', 2025, 1),
            ('Кузнецов', 'Программирование', 'ИВТ-25', 2025, 1),
            ('Морозов', 'Высшая математика', 'ИВТ-25', 2025, 1),
        ]

        for teacher_name, discipline_name, group_name, year, number in data:
            teacher = teachers[teacher_name]
            discipline = disciplines[discipline_name]
            group = groups[group_name]
            semester = semesters[(year, number)]

            obj, created = Teaching.objects.get_or_create(
                teacher=teacher, discipline=discipline, group=group, semester=semester,
            )
            self.stdout.write(f'Преподавание {obj}: {"создано" if created else "уже есть"}')

        # добираем оставшиеся дисциплины каждой группе, чтобы хватило записей на 200+ оценок
        default_teacher = teachers['Кузнецов']
        for group in groups.values():
            semester = semesters[(group.admission_year, 1)]
            assigned_disciplines = {t.discipline for t in Teaching.objects.filter(group=group)}
            for discipline in disciplines.values():
                if discipline in assigned_disciplines:
                    continue
                obj, created = Teaching.objects.get_or_create(
                    teacher=default_teacher, discipline=discipline, group=group, semester=semester,
                )
                self.stdout.write(f'Преподавание {obj}: {"создано" if created else "уже есть"}')

    def create_grades(self):
        grade_values = [
            GradeStatus.TWO, GradeStatus.THREE, GradeStatus.FOUR, GradeStatus.FIVE,
        ]

        count_created = 0
        for teaching in Teaching.objects.select_related('group'):
            students = Student.objects.filter(group=teaching.group)
            for student in students:
                value = random.choice(grade_values)
                obj, created = Grade.objects.get_or_create(
                    student=student,
                    teaching=teaching,
                    defaults={'value': value},
                )
                if created:
                    count_created += 1

        self.stdout.write(f'Создано оценок: {count_created}')