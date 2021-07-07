"""skills URL configuration.
"""

from django.urls import path

from . import views

app_name = 'skills'
urlpatterns = [
    path('', views.home, name='home'),
    path('demand-vs-knowledge/', views.demand_vs_knowledge, name='demand-vs-knowledge'),
    path('project-new/', views.project_new, name='project-new'),
    path('project/<int:project_id>/', views.project, name='project'),
    path('projects/', views.projects, name='projects'),
    path('self-assess/', views.self_assess, name='self-assess'),
    path('person/<str:login>/', views.render_person, name='person'),
    path('skill/<int:skill_id>/', views.render_skill, name='skill'),
]
