"""skills URL configuration.
"""

from django.urls import path

from . import views

app_name = 'skills'
urlpatterns = [
    path('', views.home, name='home'),
    path('assess/', views.assess),
    path('assess-done/', views.assess_done, name='assess-done'),
    path('assess-project/', views.assess_project, name='assess-project'),
    path('person/<str:login>/', views.person, name='person'),
    path('skill/<int:skill_id>/', views.skill, name='skill'),
]
