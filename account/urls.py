from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    # SignUp URL: A view to allow users to sign up (register) on the platform.
    # Name: 'signup'
    # View: SignupView
    # This URL does not require any parameters.
    path('signup/', views.SignupView.as_view(), name='signup'),

    # Login URL: A view to allow users to log in to their account.
    # Name: 'login'
    # View: LoginView
    # This URL does not require any parameters.
    path('login/', views.LoginView.as_view(), name='login'),

    # Logout URL: A view to log users out of their account.
    # Name: 'logout'
    # View: LogoutView
    # This URL does not require any parameters.
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Forget Password URL: A view for users who have forgotten their password and want to reset it.
    # Name: 'forget-pass'
    # View: ForgetPasswordView
    # This URL does not require any parameters.
    path('foget-pass/', views.ForgetPasswordView.as_view(), name='forget-pass'),

    # Reset Password URL: A view for users to reset their password using a token.
    # Name: 'reset-password'
    # View: ResetPasswordView
    # Parameters:
    #   - uidb64: A URL-safe base64 encoded user ID
    #   - token: A password reset token for verification
    path('reset-password/<uidb64>/<token>/', views.ResetPasswordView.as_view(), name='reset-password'),

    # User Profile URL: A view to display the profile of a specific user.
    # Name: 'profile-user'
    # View: ProfileUserView
    # Parameters:
    #   - user_id: The unique ID of the user whose profile is being viewed
    path('userprofile/<int:user_id>/', views.ProfileUserView.as_view(), name='profile-user'),

    # Comment Management URL: A view for administrators to approve or delete comments.
    # Name: 'comment-management'
    # View: CommentManagementView
    # Parameters:
    #   - comment_id: The unique ID of the comment to be managed (approved or deleted)
    path('comment/action/<int:comment_id>/', views.CommentManagementView.as_view(), name='comment-management'),
]


