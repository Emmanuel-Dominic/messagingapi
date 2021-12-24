from django.urls import path
from rest_framework_simplejwt.views import (
    TokenVerifyView
)

from . import views

app_name = 'messages-api'

urlpatterns = [
    path('token/verify/', TokenVerifyView.as_view(), name='verify'),
    path('register/', views.RegistrationAPIView.as_view(), name='register'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('users/', views.UserListAPIView.as_view(), name='users-info'),
    path('users/<user_id>/', views.UserRetrieveUpdateAPIView.as_view(), name='user-info'),
    path('clubs/', views.ClubCreateListAPIView.as_view(), name='clubs'),
    path('clubs/<club_id>/', views.ClubRetrieveUpdateDeleteAPIView.as_view(), name='club'),
    path('groups/users/list', views.ClubUserListAPIView.as_view(), name='list-groups'),
    path('groups/users/<club_id>/<user_id>', views.ClubUserCreateAPIView.as_view(), name='post-groups'),
    path('groups/<club_id>/', views.ClubUserRetrieveUpdateDeleteAPIView.as_view(), name='group'),
    path('messages/users/<user_id>/', views.UserMessageCreateListAPIView.as_view(), name='message-user'),
    path('messages/clubs/<club_id>/', views.ClubMessageCreateListAPIView.as_view(), name='message-group'),
    path('messages/<message_id>/', views.MessageRetrieveUpdateDeleteAPIView.as_view(), name='message')
]
