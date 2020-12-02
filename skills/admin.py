from django.contrib import admin
from skills.models import Category, Skill, PersonAssessment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ordering = ('name', )


@admin.register(PersonAssessment)
class PersonAssessmentAdmin(admin.ModelAdmin):
    ordering = ('-date', 'person__login')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category',)
    ordering = ('category__name', 'name')
