from django.db import models

class Specialty(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150, unique=True)
