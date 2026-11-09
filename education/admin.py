from django.contrib import admin
from education.models import *


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'group', 'education_form', 'status', 'admission_date')
    list_filter = ('group', 'education_form', 'status', 'gender')
    search_fields = ('last_name', 'first_name', 'middle_name', 'email')
    autocomplete_fields = ('group',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'course', 'admission_year', 'curator')
    list_filter = ('specialty', 'course', 'admission_year', 'curator')
    search_fields = ('name',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'department', 'position')
    list_filter = ('department', 'position', 'academic_degree')
    search_fields = ('last_name', 'first_name', 'middle_name', 'email')

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    list_filter = ('code',)
    search_fields = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('name', 'control_form')
    list_filter = ('control_form',)
    search_fields = ('name',)

@admin.register(Teaching)
class TeachingAdmin(admin.ModelAdmin):
    list_display = ('group', 'discipline')
    list_filter = ('group',)
    search_fields = ('group__name', 'discipline__name', 'teacher__last_name')
    autocomplete_fields = ('group', 'discipline', 'teacher')

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('start_year', 'number')
    list_filter = ('start_year', 'number')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'value')
    list_filter = ('assignment__teaching__semester', 'assignment__teaching__discipline', 'value')
    search_fields = ('student__last_name', 'student__first_name')
    autocomplete_fields = ('student', 'assignment')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('teaching', 'title', 'grade_type', 'weight', 'order')
    list_filter = ('grade_type',)
    search_fields = ('title', 'teaching__discipline__name')
    autocomplete_fields = ('teaching',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
