from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from . forms import SignUpForm, ForgetPasswordForm, ResetPasswordForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .decorators import redirect_if_authenticated
from django.utils.decorators import method_decorator
from . models import CustomUser, ProfileUser
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from .tasks import send_reset_email
from .forms import UserProfileForm, CustomUserForm
from core.models import Comment
from django.core.cache import cache


@method_decorator(redirect_if_authenticated, name='dispatch')
class SignupView(View):
    """
    View to handle user signup.
    Redirects authenticated users to the home page.
    Displays the signup form on GET request.
    Processes the form and creates a new user on POST request.
    """
    form_class = SignUpForm
    template_name = 'account/signup.html'
    def get(self, reqest):
        """Handles GET request to display the signup form."""
        return render(reqest, self.template_name, {'form': self.form_class()})

    def post(self, request):
        """Handles POST request to process the signup form and create a new user."""
        form = self.form_class(request.POST)
        if request.user.is_authenticated:
            messages.info(request, 'You are Already Logged in!')
            return redirect('core:home')
        if form.is_valid():
            cd = form.cleaned_data
            # Creating a new user instance using the custom user model
            user = CustomUser.objects.create_user(cd['username'], cd['email'],)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user) # Logging in the newly created user
            messages.success(request, 'Register Successfully!')
            return redirect('core:home')
        messages.error(request, 'Please enter the valid information.')
        return render(request, self.template_name, {'form': form})


@method_decorator(redirect_if_authenticated, name='dispatch')
class LoginView(View):
    """
    View to handle user login.
    Redirects authenticated users to the home page.
    Displays the login form on GET request.
    Authenticates and logs in the user on POST request.
    """
    templates_name = 'account/login.html'
    form_class = AuthenticationForm
    def get(self, request):
        """Handles GET request to display the login form."""
        return render(request, self.templates_name, {'form': self.form_class})

    def post(self, request):
        """Handles POST request to authenticate and log in the user."""
        form = self.form_class(data=request.POST)
        if request.user.is_authenticated:
            messages.info(request, 'You are Already Logged in!')
            return redirect('core:home')
        if form.is_valid():
            cd = form.cleaned_data
            username = cd['username']
            password = cd['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login Successfully')
                return redirect('core:home')
            messages.error(request, 'Username or Password is Wrong!')
            return render(request, self.templates_name, {'form': form})
        messages.error(request, 'Username or Password is Wrong!')
        return render(request, self.templates_name, {'form': form})


class LogoutView(View):
    """
    View for handling user logout.
    Ensures that only authenticated users can log out.
    """
    def get(self, request):
        if not request.user.is_authenticated:
            # Inform user if they are already logged out
            messages.info(request, 'You are Already Logged out!')
            return redirect('core:home')
        # Log out the user and display a success message
        logout(request)
        messages.success(request, 'Logout Successfully')
        return redirect('core:home')


class ForgetPasswordView(View):
    """
    View for handling the forget password process.
    Renders the forget password form and processes the request to send a password reset link.
    """
    template_name = 'account/forget-password.html'
    form_class = ForgetPasswordForm
    def get(self, request):
        """Handles GET request to display the forget password form."""
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request):
        """Handles POST request to process the forget password form submission."""
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.id))
                # Generate password reset link
                domain = get_current_site(request).domain
                reset_link = f'http://{domain}/account/reset-password/{uid}/{token}'
                print(reset_link)
                # Send reset email asynchronously
                send_reset_email.delay('Password Reset Request from FREEWORDS', email, reset_link, user.username)

                messages.info(request, 'Please check your email. we send you a link to resting your password!')
                return redirect('core:home')
            except CustomUser.DoesNotExist:
                messages.error(request, 'Your email is wrong!')
                return render(request, self.template_name, {'form': form})
        messages.error(request, 'Please enter the valid information!')
        return render(request, self.template_name, {'form': form})


class ResetPasswordView(View):
    """
    View for handling password reset.
    Renders the reset password form and processes the new password submission.
    """
    template_name = 'account/reset-password.html'
    form_class = ResetPasswordForm

    def get(self, request, uidb64, token):
        """Handles GET request to display the password reset form."""
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                form = self.form_class()
                return render(request, self.template_name, {'form': form, 'uidb64': uidb64, 'token': token})
            messages.error(request, "The reset link is invalid or expired.")
            return redirect('account:login')
        except(ValueError, OverflowError, CustomUser.DoesNotExist):
            messages.error(request, "The reset link is invalid or expired.")
            return redirect('account:login')


    def post(self, request, uidb64, token):
        """Handles POST request to process the password reset submission."""
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = CustomUser.objects.get(pk=uid)
                if default_token_generator.check_token(user, token):
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                    messages.success(request, "Your password has been reset successfully!")
                    return redirect('account:login')
                else:
                    messages.error(request, "The reset link is invalid or expired.")
            except (ValueError, OverflowError, CustomUser.DoesNotExist):
                messages.error(request, "An error occurred. Please try again.")
                return render(request, self.template_name, {'form': form, 'uidb64': uidb64, 'token': token})
        messages.error(request, "An error occurred. Please try again.")
        return render(request, self.template_name, {'form': form, 'uidb64': uidb64, 'token': token})


class ProfileUserView(View):
    """
    View for displaying and updating a user's profile.
    Caches user and profile data to optimize performance.
    """
    template_name = 'account/profile.html'

    def get(self, request, user_id):
        """Handles GET request to display the user's profile."""
        custom_user_cache_key = f'custom_user_info_{user_id}'
        custom_user = cache.get(custom_user_cache_key)

        if not custom_user:
            custom_user = get_object_or_404(CustomUser, id=user_id)
            cache.set(custom_user_cache_key, custom_user, timeout=43200)

        profile_user_cache_key = f'profile_user_info_{user_id}'
        profile_user = cache.get(profile_user_cache_key)

        if not profile_user:
            profile_user, created = ProfileUser.objects.get_or_create(user=custom_user)
            cache.set(profile_user_cache_key, profile_user, timeout=43200)

        user_form = CustomUserForm(instance=custom_user)
        profile_form = UserProfileForm(instance=profile_user)

        # Cache approved comments and replies
        comment_cache_key = 'approved_comments_in_admin_profile'
        comments = cache.get(comment_cache_key)

        if not comments:
            comments = list(Comment.objects.filter(is_approved=False, is_reply=False))
            cache.set(comment_cache_key, comments, timeout=43200)

        reply_cache_key = 'approved_reply_in_admin_profile'
        replies = cache.get(reply_cache_key)

        if not replies:
            replies = list(Comment.objects.filter(is_reply=True, is_approved=False))
            cache.set(reply_cache_key, replies, timeout=43200)

        return render(request, self.template_name, {
            'profile': profile_user,
            'user_form': user_form,
            'profile_form': profile_form,
            'comments': comments,
            'replies': replies,
        })

    def post(self, request, user_id):
        """Handles POST request to update user's profile information."""
        custom_user = get_object_or_404(CustomUser, id=user_id)
        profile_user = get_object_or_404(ProfileUser, user=custom_user)
        user_form = CustomUserForm(request.POST, instance=custom_user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile_user)

        # Handle profile picture update
        if 'photo' in request.FILES:
            if profile_form.is_valid():
                profile_user.profile_picture = request.FILES['photo']
                profile_user.save()

                cache.delete(f'profile_user_info_{user_id}')
                cache.delete(f'custom_user_info_{user_id}')

                messages.success(request, 'Your profile picture has been updated!')
                return redirect('account:profile-user', user_id=user_id)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            cache.delete(f'profile_user_info_{user_id}')
            cache.delete(f'custom_user_info_{user_id}')

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('account:profile-user', user_id=user_id)
        messages.error(request, 'Please correct the errors below.')
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
        })


class CommentManagementView(View):
    """
    View for managing comments and replies.
    Allows admin users to approve or delete comments and replies.
    """
    def post(self, request, comment_id):
        # Check if the user is an admin
        if request.user.is_staff:
            action = request.POST.get('action')
            comment = get_object_or_404(Comment, id=comment_id)

            if action == 'approve':
                # Approving a comment
                comment.is_approved = True
                comment.save()
                cache.delete(f"approved_comments_{comment.post.id}")
                messages.success(request, 'Comment approved successfully.')

            elif action == 'delete':
                # Deleting a comment
                cache.delete(f"approved_comments_{comment.post.id}")
                comment.delete()
                messages.success(request, 'Comment deleted successfully.')

            elif action == 'approve_reply':
                # Approving a reply
                comment.is_approved = True
                comment.save()
                cache.delete(f"approved_comments_{comment.post.id}")
                messages.success(request, 'Reply approved successfully.')

            elif action == 'delete_reply':
                # Deleting a reply
                cache.delete(f"approved_comments_{comment.post.id}")
                comment.delete()
                messages.success(request, 'Reply deleted successfully.')

            return redirect('account:profile-user', user_id=request.user.id)

        # If the user is not an admin, show an error message
        messages.error(request, 'Sorry! you are not Admin')
        return redirect('core:home')
