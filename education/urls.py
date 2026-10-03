from django.urls import path
from . import api

api_urlpatterns = [
    path('groups/', api.groups_api, name='groups_api'),
]

urlpatterns = [
    # сюда позже добавятся обычные Django-страницы, если будут
]