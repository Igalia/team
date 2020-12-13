from django.contrib import admin

from ballots.models import Ballot


@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
    ordering = ('-created', )
