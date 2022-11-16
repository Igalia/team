from django.contrib import admin
from django.db import models
from django.db.models.functions import Lower
from django.forms.widgets import CheckboxSelectMultiple

from people.models import Level, Person, Team, PersonalData


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'level',)
    ordering = (Lower('login'), )
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


@admin.register(PersonalData)
class PersonalDataAdmin(admin.ModelAdmin):
    ordering = (Lower('person__login'), )


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    ordering = ('value', )


@admin.register(Team)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug')
    prepopulated_fields = {'slug': ('name', )}
    ordering = ('name', )
