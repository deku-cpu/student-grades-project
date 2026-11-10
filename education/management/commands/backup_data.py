from pathlib import Path

from django.core.management.base import BaseCommand
from education.backups import write_backup


class Command(BaseCommand):
    help = 'Сохраняет резервную копию данных в JSON'

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *args, **options):
        path = Path(options['filename'])
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8') as output:
            write_backup(output)
        self.stdout.write(self.style.SUCCESS(f'Резервная копия сохранена: {path}'))
