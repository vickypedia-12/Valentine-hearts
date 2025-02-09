from django.urls import path
from . import views

app_name = 'hearts'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('questionnaire/', views.questionnaire, name='questionnaire'),
    path('matches/', views.matches, name='matches'),
    path('reveal-match/<int:match_id>/', views.reveal_match, name='reveal_match'),
    path('messages/', views.messages, name='messages'),
    path('confessions/', views.confessions, name='confessions'),
]