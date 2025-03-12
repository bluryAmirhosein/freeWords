from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('foget-pass/', views.ForgetPasswordView.as_view(), name='forget-pass'),
    path('reset-password/<uidb64>/<token>/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('userprofile/<int:user_id>/', views.ProfileUserView.as_view(), name='profile-user'),
    path('comment/action/<int:comment_id>/', views.CommentManagementView.as_view(), name='comment-management')

]

