"""Polls URL configuration.
"""

from django.urls import path

from . import views

app_name = 'ballots'
urlpatterns = [
    path('', views.home, name='home'),
    path('new/', views.new, name='new'),
    path('edit/<int:ballot_id>/', views.edit, name='edit'),
    path('delete/<int:ballot_id>/', views.delete, name='delete'),
    path('ballot/<int:ballot_id>/', views.ballot, name='ballot'),
    path('retract_vote/<int:ballot_id>/', views.retract_vote, name='retract_vote'),
    path('markdownify/', views.markdownify, name='markdownify'),
]
