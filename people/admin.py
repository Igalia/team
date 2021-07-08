from django.contrib import admin
from people.models import Level, Person, Team


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'level',)
    ordering = ('login', )


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    ordering = ('value', )


@admin.register(Team)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    ordering = ('name', )
