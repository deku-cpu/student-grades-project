import datetime
from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def repair_zero_weights(apps, schema_editor):
    # В старом целочисленном поле значение по умолчанию 0.1 сохранялось как 0.
    apps.get_model('education', 'Assignment').objects.filter(weight=0).update(weight=1)
    grades = apps.get_model('education', 'Grade').objects.filter(
        assignment__grade_type='final', assignment__teaching__discipline__control_form='credit')
    grades.filter(value='2').update(value='fail')
    grades.filter(value__in=['3', '4', '5']).update(value='pass')
    apps.get_model('auth', 'User').objects.filter(profile__role='admin').update(is_staff=True)


class Migration(migrations.Migration):
    dependencies = [
        ('education', '0006_alter_student_date_of_birth'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(name='AuditLog', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('action', models.CharField(max_length=30)),
            ('path', models.CharField(max_length=255)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
        ], options={'verbose_name': 'Действие пользователя', 'verbose_name_plural': 'Журнал действий', 'ordering': ['-created_at', '-id']}),
        migrations.AlterModelOptions(name='assignment', options={'ordering': ['order', 'id']}),
        migrations.AlterField(model_name='assignment', name='weight', field=models.DecimalField(decimal_places=2, default=Decimal('1'), max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.01')), django.core.validators.MaxValueValidator(Decimal('100'))])),
        migrations.RunPython(repair_zero_weights, migrations.RunPython.noop),
        migrations.AlterField(model_name='semester', name='start_year', field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(2000), django.core.validators.MaxValueValidator(2100)])),
        migrations.AlterField(model_name='student', name='date_of_birth', field=models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(1900, 1, 1)), django.core.validators.MaxValueValidator(datetime.date.today)])),
        migrations.AlterField(model_name='student', name='middle_name', field=models.CharField(blank=True, max_length=100)),
        migrations.AlterField(model_name='student', name='phone_number', field=models.CharField(blank=True, max_length=12, validators=[django.core.validators.RegexValidator(r'^\+?\d{10,11}$', 'Введите телефон из 10–11 цифр, можно с +')])),
        migrations.AlterField(model_name='teacher', name='academic_degree', field=models.CharField(blank=True, choices=[('candidate_of_sciences', 'Кандидат Наук'), ('doctor_of_science', 'Доктор Наук')], max_length=30)),
        migrations.AlterField(model_name='teacher', name='middle_name', field=models.CharField(blank=True, max_length=100)),
        migrations.AlterField(model_name='teacher', name='phone_number', field=models.CharField(blank=True, max_length=12, validators=[django.core.validators.RegexValidator(r'^\+?\d{10,11}$', 'Введите телефон из 10–11 цифр, можно с +')])),
        migrations.AddConstraint(model_name='grade', constraint=models.CheckConstraint(condition=models.Q(value__in=['2', '3', '4', '5', 'pass', 'fail']), name='valid_grade_value')),
    ]
