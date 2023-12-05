"""URL configuration of the People application.

This is the main section for the URL map. See also `.root_urls.py`.
"""

from django.http.response import HttpResponseRedirect
from django.urls import path, reverse

from common.auth import get_user_login
from . import views


def home(request):
    return HttpResponseRedirect(reverse('root:person', args=[get_user_login(request)]))


app_name = 'people'
urlpatterns = [
    # Convenience view that redirects to one of meaningful URLs.
    path('', home, name='home'),

    # New contribution form.  The new contribution will be created for the user that is currently logged in.
    path('contribution/new/', views.new_contribution, name='contribution-new'),
    # Shows a single contribution, and allows editing it if it belongs to the user that is currently logged in.
    path('contribution/<int:contribution_id>/', views.render_contribution, name='contribution'),
    # Shows contributions of a person with `login`.
    path('contributions/<str:login>/', views.render_contributions, name='contributions'),

    # Sets the current team (stores it in the session).
    path('<str:login>', views.render_person, name='person'),
    # People picker.
    path('picker/', views.picker, name='picker'),

    # Shows details of a single team.
    path('team/<str:team_slug>/', views.render_team, name='team'),
    # Shows all teams.
    path('teams/', views.render_teams, name='teams'),
]
