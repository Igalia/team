"""skills URL configuration.
"""

from django.urls import path

from . import views

app_name = 'skills'
urlpatterns = [
    # Views that require the user to be in some team.
    path('', views.home, name='home'),
    path('demand-vs-knowledge/', views.demand_vs_knowledge, name='demand-vs-knowledge'),
    path('project-new/', views.project_new, name='project-new'),
    path('projects/', views.projects, name='projects'),
    path('self-assess/', views.self_assess, name='self-assess'),
    # Wrapper for the views in the above group.
    path('pick-teams/', views.render_pick_teams, name='pick-teams'),
    # Views that do not require the user to be in any team.
    path('project/<int:project_id>/', views.project, name='project'),
    path('person/<str:login>/', views.render_person, name='person'),
    path('skill/<int:skill_id>/', views.render_skill, name='skill'),
]
