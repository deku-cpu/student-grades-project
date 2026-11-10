import os
from .settings import *

# Обычные тесты работают в памяти. Для проверки PostgreSQL задайте TEST_DATABASE=postgres.
if os.getenv('TEST_DATABASE') != 'postgres':
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:', 'ATOMIC_REQUESTS': True}}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
