"""URL configuration of the People application.

The People application is
"""

from django.http.response import HttpResponseRedirect
from django.urls import path

from . import views


app_name = 'people'
urlpatterns = [
    # People picker.
    path('picker/', views.picker, name='picker'),
]
