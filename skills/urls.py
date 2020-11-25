"""skills URL configuration.
"""

from django.urls import path

from . import views

app_name = 'skills'
urlpatterns = [
    path('', views.skills, name='home'),
    path('skill/<int:skill_id>/', views.skill, name='skill'),
    path('assess/', views.assess),
    path('assess-done/', views.assess_done, name='assess-done'),
]
