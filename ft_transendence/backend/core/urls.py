from django.urls import path, include
from core import views as core_views
from core.views import (
    UserAPIView,
    PersonsAPIView,
    EmailValidation, 
    Confirmation, 
    Register, 
    Password,
    PasswordReset,
    ForgetConfirmation,
    Login,
    Logout,
    Home,
    Profile,
    JoinList,
    WaitingRoom,
    HistoryView,
    Leaderboard,
    CreateRoom,
    SettingsById
)

urlpatterns = [
    path('email_validation/', EmailValidation.as_view()),
    path('confirm/', Confirmation.as_view()),
    path('register/', Register.as_view()),
    path('password_reset/', PasswordReset.as_view()),
    path('forget_confirm/', ForgetConfirmation.as_view()),
    path('password/', Password.as_view()),
    path('login/', Login.as_view()),

    path('api/v1/logout/<int:pk>/', Logout.as_view()),
    path('api/v1/home/<int:pk>/', Home.as_view()),
    path('users/', UserAPIView.as_view()),
    path('api/v1/persons/<int:pk>/', PersonsAPIView.as_view()),
    path('api/v1/profile/<int:pk>/', Profile.as_view()),
    path('api/v1/leaderboard/<int:pk>/', Leaderboard.as_view()),
    path('api/v1/joinlist/<int:pk>/', JoinList.as_view()),
    path('api/v1/waitingroom/<int:pk>/', WaitingRoom.as_view()),
    path('api/v1/history/<int:pk>/', HistoryView.as_view()),
    path('api/v1/settings/<int:pk>/', SettingsById.as_view()),
    path('api/v1/createroom/<int:pk>/', CreateRoom.as_view()),
]
