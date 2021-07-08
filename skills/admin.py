from django.contrib import admin
from django.db import models
from django.forms.widgets import CheckboxSelectMultiple

from skills.models import Category, PersonAssessment, Project, ProjectFocusRecord, Skill


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ordering = ('name', )
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


@admin.register(PersonAssessment)
class PersonAssessmentAdmin(admin.ModelAdmin):
    ordering = ('-date', 'person__login')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date', 'active')
    ordering = ('-date', 'name')
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


@admin.register(ProjectFocusRecord)
class ProjectAdmin(admin.ModelAdmin):
    ordering = ('project__name', 'skill__name')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category',)
    ordering = ('category__name', 'name')
