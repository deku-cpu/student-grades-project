from django.db import models


class AuditLog(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=30)
    path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = 'Действие пользователя'
        verbose_name_plural = 'Журнал действий'

    def __str__(self):
        return f'{self.created_at}: {self.user} — {self.action}'
