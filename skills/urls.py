"""skills URL configuration.
"""

from django.urls import path

from . import views

app_name = 'skills'
urlpatterns = [
    # Convenience view that redirects to one of meaningful URLs.
    path('', views.home, name='home'),
    # Sets the current team (stores it in the session).
    # Recognises two special values for 1) showing data for all teams and 2) resetting the view to the teams of the
    # current user.
    path('set-current-team/<str:team_slug>/', views.set_current_team, name='set-current-team'),

    # Team diagrams show data for the teams of the current user.  That requires the user to be in some (at least one)
    # team.  If that is not the case, these views redirect to the team picker.

    # Team diagram of interest versus knowledge.
    path('interest-vs-knowledge/', views.interest_vs_knowledge, name='interest-vs-knowledge'),
    # Team diagram of market demand versus knowledge and interest.
    path('demand-vs-knowledge/', views.demand_vs_knowledge, name='demand-vs-knowledge'),
    # Team portfolio (list of all projects and their focus).
    path('projects/', views.projects, name='projects'),
    # New project form.
    path('project-new/', views.project_new, name='project-new'),
    # Self-assessment form.
    path('self-assess/', views.self_assess, name='self-assess'),

    # Wrapper for the views in the above group.  Shows the team selection form if the current user is not listed in any.
    path('pick-teams/', views.render_pick_teams, name='pick-teams'),

    # Views that do not require the user to be in any team.

    # Shows a single project.  Optionally allows editing it.
    path('project/<int:project_id>/', views.project, name='project'),
    # Shows skills of a single person.
    path('person/<str:login>/', views.render_person, name='person'),
    # Shows data for a single skill: who knows it, and who is interested in it.
    path('skill/<int:skill_id>/', views.render_skill, name='skill'),

    # Team diagram of interest versus knowledge for the particular team, or for all teams.
    path('interest-vs-knowledge/<str:team_slug>/', views.interest_vs_knowledge_for_team,
         name='interest-vs-knowledge-for-team'),
    # Team diagram of market demand versus  knowledge and interest for the particular team.
    path('demand-vs-knowledge/<str:team_slug>/', views.demand_vs_knowledge_for_team,
         name='demand-vs-knowledge-for-team'),
    # Team portfolio (list of all projects and their focus) for the particular team.
    path('projects/<str:team_slug>/', views.projects_for_team, name='projects-for-team'),
]
