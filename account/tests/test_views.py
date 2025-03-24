from django.test import TestCase, Client, RequestFactory
from account.models import CustomUser, ProfileUser
from core.models import Comment, BlogPost
from django.urls import reverse
from django.contrib.messages import get_messages
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


class LoginViewTest(TestCase):
    """
    Test suite for the Login view.
    It covers various scenarios including valid and invalid logins,
    redirections, and handling inactive users.
    """
    def setUp(self):
        """Set up test client, test user, and login URL."""
        self.client = Client()
        self.url = reverse('account:login')
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'
        )

    def test_login_view(self):
        """Test if the login page loads successfully and uses the correct template."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_post_valid_login(self):
        """Test successful login with valid credentials."""
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'testpass123'})
        self.assertRedirects(response, reverse('core:home'))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Login Successfully', messages)
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'testuser')

    def test_post_invalid_login(self):
        """Test login failure with incorrect credentials."""
        response = self.client.post(self.url, {'username': 'wronguser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username or Password is Wrong!')
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

    def test_authenticated_user_redirect(self):
        """Test that an already logged-in user is redirected from login page to home."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('core:home'))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('You are Already Logged in!', messages)

    def test_invalid_form(self):
        """Test login attempt with an empty form submission."""
        response = self.client.post(self.url, {'username': '', 'password': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username or Password is Wrong!')

    def test_inactive_user_login(self):
        """Test login attempt with an inactive user account."""
        inactive_user = CustomUser.objects.create_user(username='inactiveuser', password='testpass123', is_active=False)
        response = self.client.post(self.url, {'username': 'inactiveuser', 'password': 'testpass123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username or Password is Wrong!')
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)


class LogoutViewTest(TestCase):
    """
    Test suite for the Logout view.
    It covers logging out both authenticated and unauthenticated users.
    """
    def setUp(self):
        """Set up test client, test user, and logout URL."""
        self.client = Client()
        self.url = reverse('account:logout')
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass123')

    def test_logout_authenticated_user(self):
        """Test if an authenticated user is logged out and redirected to home."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('core:home'))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Logout Successfully', messages)
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

    def test_logout_unauthenticated_user(self):
        """Test if an unauthenticated user is redirected when trying to log out."""
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('core:home'))

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('You are Already Logged out!', messages)  # Proper message should be displayed


class ForgetPasswordViewTest(TestCase):
    """
    Test suite for the Forget Password view.
    It covers rendering the password reset form, handling valid and invalid submissions.
    """
    def setUp(self):
        """Set up test user and password reset URL."""
        self.url = reverse('account:forget-pass')
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'
        )

    def test_get_request_renders_form(self):
        """Test if the password reset page loads successfully and contains a form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/forget-password.html')
        self.assertContains(response, '<form')

    def test_post_request_with_valid_email_redirects(self):
        """Test if submitting a valid email redirects the user to the home page."""
        data = {'email': 'testuser@email.com'}
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('core:home'))

    def test_post_request_with_invalid_email_shows_error(self):
        """Test if submitting an invalid email shows an error message."""
        data = {'email': 'invalid@example.com'}
        response = self.client.post(self.url, data)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Your email is wrong!')
        self.assertTemplateUsed(response, 'account/forget-password.html')

    def test_post_request_with_invalid_form_shows_error(self):
        """Test if submitting an invalid form (e.g., incorrect email format) shows an error."""
        data = {'email': 'invalid-email'}
        response = self.client.post(self.url, data)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Please enter the valid information!')
        self.assertTemplateUsed(response, 'account/forget-password.html')


class ResetPasswordViewTest(TestCase):
    """
    Test suite for the Reset Password view.
    It covers various scenarios including valid and invalid password reset attempts.
    """
    def setUp(self):
        """Set up test user, token, and reset password URL."""
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='oldpassword')
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = reverse('account:reset-password', args=[self.uidb64, self.token])

    def test_get_valid_link(self):
        """Test if a valid reset password link renders the reset form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reset Password')

    def test_get_invalid_link(self):
        """Test if an invalid reset password link redirects to the login page."""
        invalid_url = reverse('account:reset-password', args=['invaliduid', 'invalidtoken'])
        response = self.client.get(invalid_url)
        self.assertRedirects(response, reverse('account:login'))

    def test_post_valid_password(self):
        """Test if submitting a valid new password updates the user's password."""
        response = self.client.post(self.url, {'password': 'newsecurepassword', 'confirm_password': 'newsecurepassword'})
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newsecurepassword'))
        self.assertRedirects(response, reverse('account:login'))

    def test_post_invalid_password(self):
        """Test if submitting an invalid password (empty field) shows an error message."""
        response = self.client.post(self.url, {'password': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An error occurred. Please try again.')

    def test_user_not_found(self):
        """Test if trying to reset the password for a non-existing user fails."""
        invalid_uid = urlsafe_base64_encode(force_bytes(999))
        url = reverse('account:reset-password', args=[invalid_uid, self.token])
        response = self.client.post(url, {'password': 'newpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An error occurred. Please try again.')


class ProfileUserViewTests(TestCase):
    """
    Test suite for testing views related to user profiles.
    It performs tests for GET and POST requests, checking for both successful and edge cases.
    """
    def setUp(self):
        """Set up test user, profile, and URL."""
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.profile = ProfileUser.objects.create(user=self.user)
        self.url = reverse('account:profile-user', args=[self.user.id])
        self.client.login(username='testuser', password='password')

    def test_get_profile_page(self):
        """Test if the profile page renders correctly."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/profile.html')
        self.assertIn('profile', response.context)
        self.assertIn('user_form', response.context)
        self.assertIn('profile_form', response.context)

    def test_profile_cache(self):
        """Test if the profile is cached correctly."""
        cache_key = f'profile_user_info_{self.user.id}'
        cache.set(cache_key, self.profile, timeout=43200)
        cached_profile = cache.get(cache_key)
        self.assertEqual(cached_profile, self.profile)

    def test_comment_cache(self):
        """Test if comments are cached correctly."""
        post = BlogPost.objects.create(title_heading="Test Post", title_description="Test Description")
        comment = Comment.objects.create(user=self.user, post=post, content='Test comment', is_approved=False)
        cache_key = 'approved_comments_in_admin_profile'
        cache.set(cache_key, [comment], timeout=43200)
        cached_comments = cache.get(cache_key)
        self.assertIn(comment, cached_comments)

    def test_post_update_profile_success(self):
        """Test if profile updates successfully."""
        data = {'full_name': 'New Name', 'bio': 'Updated bio'}
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.full_name, 'New Name')
        self.assertEqual(self.profile.bio, 'Updated bio')
        self.assertRedirects(response, self.url)

    def test_cache_clear_on_update(self):
        """Test if cache is cleared after profile update."""
        cache.set(f'profile_user_info_{self.user.id}', self.profile)
        cache.set(f'custom_user_info_{self.user.id}', self.user)
        data = {'full_name': 'Updated Name', 'bio': 'New Bio'}
        self.client.post(self.url, data)
        self.assertIsNone(cache.get(f'profile_user_info_{self.user.id}'))
        self.assertIsNone(cache.get(f'custom_user_info_{self.user.id}'))


class CommentManagementViewTest(TestCase):
    """
    Test suite for managing comments (approve, delete) and replies in the comment management view.
    """
    def setUp(self):
        """Set up test users, comments, replies, and the URL for comment management."""
        self.client = Client()

        self.user = CustomUser.objects.create_user(username='user', password='testpass',
                                                   full_name='Test User', email='user@example.com')
        self.admin_user = CustomUser.objects.create_user(username='admin', email='admin@example.com',
                                                         password='adminpass', is_staff=True)

        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

        self.post = BlogPost.objects.create(title_heading='Test Post', title_description='Description',
                                            cover_image=cover_image, description='Content')

        self.comment = Comment.objects.create(post=self.post, user=self.user, content='Test Comment')

        self.reply = Comment.objects.create(post=self.post,user=self.user, content='Test Reply',
                                            reply=self.comment, is_reply=True)
        cache.clear()
        self.url = reverse('account:comment-management', args=[self.comment.id])

    def test_access_by_non_admin(self):
        """Test if non-admin users are redirected when trying to approve a comment."""
        self.client.login(username='user', password='testpass')
        response = self.client.post(self.url, {'action': 'approve'})
        self.assertRedirects(response, reverse('core:home'))
        self.comment.refresh_from_db()
        self.assertFalse(self.comment.is_approved)

    def test_approve_comment_by_admin(self):
        """Test if an admin can approve a comment."""
        self.client.login(username='admin', password='adminpass')
        cache_key = f"approved_comments_{self.post.id}"
        cache.set(cache_key, 'test_value')

        response = self.client.post(self.url, {'action': 'approve'})

        updated_comment = Comment.objects.get(id=self.comment.id)
        self.assertTrue(updated_comment.is_approved)

        self.assertIsNone(cache.get(cache_key))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Comment approved successfully.')


    def test_delete_comment_by_admin(self):
        """Test if an admin can delete a comment."""
        self.client.force_login(self.admin_user)

        cache_key = f"approved_comments_{self.post.id}"
        cache.set(cache_key, 'test_value')

        response = self.client.post(reverse('account:comment-management', args=[self.comment.id]), {'action': 'delete'})

        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=self.comment.id)

        self.assertIsNone(cache.get(cache_key))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Comment deleted successfully.')

    def test_approve_reply_by_admin(self):
        """Test if an admin can approve a reply."""
        self.client.force_login(self.admin_user)

        cache_key = f"approved_comments_{self.post.id}"
        cache.set(cache_key, 'test_value')

        response = self.client.post(reverse('account:comment-management', args=[self.reply.id]), {'action': 'approve_reply'})

        updated_reply = Comment.objects.get(id=self.reply.id)
        self.assertTrue(updated_reply.is_approved)

        self.assertIsNone(cache.get(cache_key))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Reply approved successfully.')

    def test_delete_reply_by_admin(self):
        """Test if an admin can delete a reply."""
        self.client.force_login(self.admin_user)

        cache_key = f"approved_comments_{self.post.id}"
        cache.set(cache_key, 'test_value')

        response = self.client.post(reverse('account:comment-management', args=[self.reply.id]), {'action': 'delete_reply'}, follow=True)

        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=self.reply.id)

        self.assertIsNone(cache.get(cache_key))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Reply deleted successfully.')

