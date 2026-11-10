import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from education.models import Student, Teacher, Profile
from education.choices import UserRole


class Command(BaseCommand):
    help = 'Создаёт аккаунты студентов и преподавателей; --demo добавляет две демонстрационные роли'

    def add_arguments(self, parser):
        parser.add_argument('--password', default=os.getenv('DEMO_PASSWORD', 'change_password123'))
        parser.add_argument('--demo', action='store_true')

    def handle(self, *args, **options):
        for model, role in ((Student, UserRole.STUDENT), (Teacher, UserRole.TEACHER)):
            for person in model.objects.filter(user__isnull=True):
                if User.objects.filter(username=person.email).exists():
                    raise CommandError(f'Логин {person.email} уже занят. Свяжите запись с пользователем через панель администратора')
                user = User.objects.create_user(username=person.email, email=person.email, password=options['password'])
                Profile.objects.create(user=user, role=role)
                person.user = user
                person.save(update_fields=['user'])
                self.stdout.write(f'{person}: аккаунт создан')
        if options['demo']:
            for username, role in (('dean', UserRole.DEANS_OFFICE), ('admin', UserRole.ADMIN)):
                user, created = User.objects.get_or_create(username=username)
                if created:
                    user.set_password(options['password'])
                    user.save()
                    Profile.objects.create(user=user, role=role)
                    self.stdout.write(f'{username}: демонстрационный аккаунт создан')
                elif user.is_superuser or getattr(getattr(user, 'profile', None), 'role', None) == role:
                    self.stdout.write(f'{username}: уже существует, пароль сохранён')
                else:
                    raise CommandError(f'Демонстрационный логин {username} занят пользователем другой роли')
