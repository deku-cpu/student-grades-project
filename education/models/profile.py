from django.db import models
from django.contrib.auth.models import User
from education.choices import UserRole

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=UserRole.choices)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.role == UserRole.ADMIN and not self.user.is_staff:
            self.user.is_staff = True
            self.user.save(update_fields=['is_staff'])

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'
