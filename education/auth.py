from django.contrib.auth.backends import ModelBackend

from .access import user_role
from .choices import UserRole


class RoleBackend(ModelBackend):
    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.is_active and user_role(user_obj) == UserRole.ADMIN:
            return True
        return super().has_perm(user_obj, perm, obj)

    def has_module_perms(self, user_obj, app_label):
        if user_obj.is_active and user_role(user_obj) == UserRole.ADMIN:
            return True
        return super().has_module_perms(user_obj, app_label)
