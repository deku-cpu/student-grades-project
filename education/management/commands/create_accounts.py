from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from education.models import Student, Teacher, Profile
from education.choices import UserRole

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.create_accounts_students()
        self.create_accounts_teachers()

    def create_accounts_students(self):
        for student in Student.objects.filter(user__isnull=True):
            user, created = User.objects.get_or_create(
                username=student.email,
                defaults={'email': student.email},
            )
            if created:
                user.set_password('change_password123')
                user.save()

            Profile.objects.get_or_create(user=user, defaults={'role': UserRole.STUDENT})

            student.user = user
            student.save()

            self.stdout.write(f'Студент {student}: аккаунт {"создан" if created else "уже был"}')

    def create_accounts_teachers(self):
        for teacher in Teacher.objects.filter(user__isnull=True):
            user, created = User.objects.get_or_create(
                username=teacher.email,
                defaults={'email': teacher.email},
            )
            if created:
                user.set_password('change_password123')
                user.save()

            Profile.objects.get_or_create(user=user, defaults={'role': UserRole.TEACHER})

            teacher.user = user
            teacher.save()

            self.stdout.write(f'Преподаватель {teacher}: аккаунт {"создан" if created else "уже был"}')