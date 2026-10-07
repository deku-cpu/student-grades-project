from django.urls import path
from . import api

api_urlpatterns = [
    path('groups/', api.groups_api, name='groups_api'),
    path('login/', api.login_api, name='login_api'),
    path('me/', api.me_api, name='me_api')
]

urlpatterns = [
    # сюда позже добавятся обычные Django-страницы, если будут
]