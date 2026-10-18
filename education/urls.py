from django.urls import path
from . import api
from . import views

api_urlpatterns = [
    path('teacher/disciplines/', api.teacher_disciplines_api, name='teacher_disciplines_api'),
    path('groups/', api.groups_api, name='groups_api'),
    path('specialities/', api.speciality_api, name='speciality_api'),
    path('login/', api.login_api, name='login_api'),
    path('me/', api.me_api, name='me_api'),
    path('logout/', api.logout_api, name='logout_api'),
    path('groups/<int:group_id>/', api.group_detail_api, name='api_group_detail'),
    path('journal/<int:teaching_id>/', api.journal_api, name='journal_api'),
    path('journal/grade/', api.grades_api, name='grade_api'),
]

urlpatterns = [
    path('journal/<int:teaching_id>/', views.journal_page, name='journal_page'),
    path('login/', views.login_page, name='login'),
    path('groups/', views.groups_page),
    path('teacher/disciplines/', views.teacher_disciplines_page, name='teacher_disciplines_page'),
]