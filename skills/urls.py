"""skills URL configuration.
"""

from django.urls import path

from . import views

app_name = 'skills'
urlpatterns = [
    path('', views.skills),
    path('assess/', views.assess),
    path('assess-done/', views.assess_done, name='assess-done'),
]
