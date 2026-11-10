from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from education.choices import GradeType
from decimal import Decimal

class Assignment(models.Model):
    # Назначение группе работы 
    # Assignment (Работа/контрольная точка) — teaching (FK), title ("Лабораторная №1"), grade_type (лабораторная/контрольная/курсовая/итоговая, через choices), weight (вес в итоговой оценке), order (порядок колонки в журнале)
    teaching = models.ForeignKey('Teaching', on_delete=models.PROTECT, related_name='assignments')
    title = models.CharField(max_length=50)
    grade_type = models.CharField(max_length=15, choices=GradeType.choices)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1'), validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100'))])
    order = models.PositiveSmallIntegerField(default=0)
    date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['teaching', 'title'], name='unique_assignment_title'),
        ]

    def __str__(self):
        return f'{self.teaching} — {self.title}'
