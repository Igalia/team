"""URL configuration of the People application.

The People application is
"""

from django.http.response import HttpResponseRedirect
from django.urls import path, reverse

from common.auth import get_user_login
from . import views


# noinspection PyUnusedLocal
def home(request):
    return HttpResponseRedirect(reverse('people:person', args=[get_user_login(request)]))


app_name = 'people'
urlpatterns = [
    # Convenience view that redirects to one of meaningful URLs.
    path('', home, name='home'),
    # Sets the current team (stores it in the session).
    path('<str:login>', views.person, name='person'),
    # People picker.
    path('picker/', views.picker, name='picker'),
]
