from django.contrib.admin import AdminSite

from .access import user_role
from .choices import UserRole


class EducationAdminSite(AdminSite):
    site_header = 'Учёт успеваемости студентов'
    site_title = 'Администрирование'

    def has_permission(self, request):
        return request.user.is_active and user_role(request.user) == UserRole.ADMIN
