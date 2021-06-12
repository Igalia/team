from django.contrib import admin

from skills.models import Category, PersonAssessment, Project, ProjectFocusRecord, Skill


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ordering = ('name', )


@admin.register(PersonAssessment)
class PersonAssessmentAdmin(admin.ModelAdmin):
    ordering = ('-date', 'person__login')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date', 'active')
    ordering = ('-date', 'title')


@admin.register(ProjectFocusRecord)
class ProjectAdmin(admin.ModelAdmin):
    ordering = ('project__title', 'skill__name')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category',)
    ordering = ('category__name', 'name')
