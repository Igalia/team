"""URL configuration of the People application.

The People application provides a couple of "root" URL for showing personal pages.  These are the "/" which shows the
personal page of the current user and "/<person-login>" which show pages of other people.

Due to how the URL resolver logic works, this sub-section is assigned to a virtual `root` application name.
"""

from django.http.response import HttpResponseRedirect
from django.urls import path, reverse

from common.auth import get_user_login
from . import views


# noinspection PyUnusedLocal
def home(request):
    return HttpResponseRedirect(reverse('root:person', args=[get_user_login(request)]))


app_name = 'root'
urlpatterns = [
    # Redirects to the personal page of "ourselves" (the current user).
    path('', home, name='home'),
    # Shows a personal page of a person with `login`.
    path('<str:login>', views.render_person, name='person'),
]