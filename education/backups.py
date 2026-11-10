from django.core.management import call_command


def write_backup(output):
    call_command('dumpdata', exclude=['contenttypes', 'auth.permission', 'sessions.session'],
                 natural_foreign=True, natural_primary=True, indent=2, stdout=output)
