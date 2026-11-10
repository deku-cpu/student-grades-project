from django.urls import path
from . import api
from . import views
from . import reports

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
    path('students/', api.students_api, name='students_api'),
    path('students/<int:student_id>/', api.student_detail_api, name='student_detail_api'),
    path('teachers/', api.teachers_api, name='teachers_api'),
    path('teachers/<int:teacher_id>/', api.teacher_detail_api, name='teacher_detail_api'),
    path('teachings/', api.teachings_api, name='teachings_api'),
    path('teachings/<int:teaching_id>/', api.teaching_detail_api, name='teaching_detail_api'),
    path('teachings/<int:teaching_id>/assignments/', api.assignments_api, name='assignments_api'),
    path('assignments/<int:assignment_id>/', api.assignment_detail_api, name='assignment_detail_api'),
    path('student/diary/', api.student_diary_api, name='student_diary_api'),
    path('student/rating/', reports.student_rating_api, name='student_rating_api'),
    path('references/<str:reference>/', api.reference_api, name='reference_api'),
    path('references/<str:reference>/<int:object_id>/', api.reference_api, name='reference_detail_api'),
    path('admin/audit/', api.audit_api, name='audit_api'),
    path('admin/backup/', api.backup_api, name='backup_api'),
    path('disciplines/', api.disciplines_api, name='disciplines_api'),
    path('disciplines/<int:discipline_id>/', api.discipline_detail_api, name='discipline_detail_api'),

    path('reports/statement/', reports.report_statement_api, name='report_statement_api'),
    path('reports/student-summary/', reports.report_student_summary_api, name='report_student_summary_api'),
    path('reports/group-rating/', reports.report_group_rating_api, name='report_group_rating_api'),
    path('reports/debtors/', reports.report_debtors_api, name='report_debtors_api'),
    path('reports/statistics/', reports.report_statistics_api, name='report_statistics_api'),
    path('reports/quality/', reports.report_quality_api, name='report_quality_api'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('journal/<int:teaching_id>/', views.journal_page, name='journal_page'),
    path('login/', views.login_page, name='login_page'),
    path('groups/', views.groups_page, name = 'groups_page'),
    path('teacher/disciplines/', views.teacher_disciplines_page, name='teacher_disciplines_page'),
    path('students/', views.students_page, name='students_page'),
    path('students/<int:student_id>/card/', views.student_card_page, name='student_card_page'),
    path('teachers/', views.teachers_page, name='teachers_page'),
    path('teachings/', views.teachings_page, name='teachings_page'),
    path('teachings/<int:teaching_id>/assignments/', views.assignments_page, name='assignments_page'),
    path('student/diary/', views.student_diary_page, name='student_diary_page'),
    path('student/rating/', views.student_rating_page, name='student_rating_page'),
    path('specialties/', views.specialties_page, name='specialties_page'),
    path('departments/', views.departments_page, name='departments_page'),
    path('semesters/', views.semesters_page, name='semesters_page'),
    path('administration/', views.administration_page, name='administration_page'),
    path('home/', views.home, name='home'),
    path('disciplines/', views.disciplines_page, name='disciplines_page'),


    path('reports/statement/',       views.report_statement_page,       name='report_statement_page'),
    path('reports/student-summary/', views.report_student_summary_page, name='report_student_summary_page'),
    path('reports/group-rating/',    views.report_group_rating_page,    name='report_group_rating_page'),
    path('reports/debtors/',         views.report_debtors_page,         name='report_debtors_page'),
    path('reports/statistics/',      views.report_statistics_page,      name='report_statistics_page'),
    path('reports/quality/',         views.report_quality_page,         name='report_quality_page'),
]
