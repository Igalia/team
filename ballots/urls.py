"""Polls URL configuration.
"""

from django.urls import path

from . import views

app_name = 'ballots'
urlpatterns = [
    path('', views.home, name='home'),
    path('new/', views.new, name='new'),
    path('ballot/<int:ballot_id>/', views.ballot, name='ballot'),
]
