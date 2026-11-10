from django.apps import AppConfig
from django.contrib.admin import apps as admin_apps


class EducationConfig(AppConfig):
    name = 'education'


class EducationAdminConfig(admin_apps.AdminConfig):
    default = False
    default_site = 'education.admin_site.EducationAdminSite'
