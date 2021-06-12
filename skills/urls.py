"""skills URL configuration.
"""

from django.urls import path

from . import views

app_name = 'skills'
urlpatterns = [
    path('', views.home, name='home'),
    path('assess/', views.assess),
    path('assess-done/', views.assess_done, name='assess-done'),
    path('project-assess/', views.project_assess, name='project-assess'),
    path('project-assess-done/', views.project_assess_done, name='project-assess-done'),
    path('projects/', views.projects, name='projects'),
    path('person/<str:login>/', views.person, name='person'),
    path('skill/<int:skill_id>/', views.skill, name='skill'),
]
