from django.contrib import admin
from django.db import models
from django.forms.widgets import CheckboxSelectMultiple

from people.models import Level, Person, Team


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'level',)
    ordering = ('login', )
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    ordering = ('value', )


@admin.register(Team)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug')
    prepopulated_fields = {'slug': ('name', )}
    ordering = ('name', )
