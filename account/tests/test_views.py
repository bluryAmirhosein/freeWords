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
    def setUp(self):
        self.client = Client()
        self.url = reverse('account:login')
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'
        )

    def test_login_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_post_valid_login(self):
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'testpass123'})
        self.assertRedirects(response, reverse('core:home'))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Login Successfully', messages)
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'testuser')

    def test_post_invalid_login(self):
        response = self.client.post(self.url, {'username': 'wronguser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username or Password is Wrong!')
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

    def test_authenticated_user_redirect(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('core:home'))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('You are Already Logged in!', messages)

    def test_invalid_form(self):
        response = self.client.post(self.url, {'username': '', 'password': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username or Password is Wrong!')

    def test_inactive_user_login(self):
        inactive_user = CustomUser.objects.create_user(username='inactiveuser', password='testpass123', is_active=False)
        response = self.client.post(self.url, {'username': 'inactiveuser', 'password': 'testpass123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username or Password is Wrong!')
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('account:logout')
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass123')

    def test_logout_authenticated_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('core:home'))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Logout Successfully', messages)
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

    def test_logout_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('core:home'))

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('You are Already Logged out!', messages)


class ForgetPasswordViewTest(TestCase):
    def setUp(self):
        self.url = reverse('account:forget-pass')
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'
        )

    def test_get_request_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/forget-password.html')
        self.assertContains(response, '<form')

    def test_post_request_with_valid_email_redirects(self):
        data = {'email': 'testuser@email.com'}
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('core:home'))

    def test_post_request_with_invalid_email_shows_error(self):
        data = {'email': 'invalid@example.com'}
        response = self.client.post(self.url, data)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Your email is wrong!')
        self.assertTemplateUsed(response, 'account/forget-password.html')

    def test_post_request_with_invalid_form_shows_error(self):
        data = {'email': 'invalid-email'}
        response = self.client.post(self.url, data)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Please enter the valid information!')
        self.assertTemplateUsed(response, 'account/forget-password.html')


class TestResetPasswordView(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='oldpassword')
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = reverse('account:reset-password', args=[self.uidb64, self.token])

    def test_get_valid_link(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reset Password')

    def test_get_invalid_link(self):
        invalid_url = reverse('account:reset-password', args=['invaliduid', 'invalidtoken'])
        response = self.client.get(invalid_url)
        self.assertRedirects(response, reverse('account:login'))

    # def test_post_valid_password(self):
    #     response = self.client.post(self.url, {'password': 'newsecurepassword'})
    #     self.user.refresh_from_db()
    #     self.assertTrue(self.user.check_password('newsecurepassword'))
    #     self.assertRedirects(response, reverse('account:login'))

    def test_post_invalid_password(self):
        response = self.client.post(self.url, {'password': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An error occurred. Please try again.')

    # def test_post_expired_token(self):
    #     expired_url = reverse('account:reset-password', args=[self.uidb64, 'invalidtoken'])
    #     response = self.client.post(expired_url, {'password': 'newpassword'})
    #     self.assertRedirects(response, reverse('account:login'))

    def test_user_not_found(self):
        invalid_uid = urlsafe_base64_encode(force_bytes(999))
        url = reverse('account:reset-password', args=[invalid_uid, self.token])
        response = self.client.post(url, {'password': 'newpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An error occurred. Please try again.')


class ProfileUserViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(id=1, username='testuser', password='testpass', full_name='test')
        test_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.profile = ProfileUser.objects.create(user=self.user, bio='Test Bio', photo=test_image)
        self.url = reverse('account:profile-user', args=[self.user.id])

    def tearDown(self):
        cache.clear()

    def test_get_profile_view_cached_data(self):
        cache.set(f'custom_user_info_{self.user.id}', self.user)
        cache.set(f'profile_user_info_{self.user.id}', self.profile)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Bio')

    def test_get_profile_view_no_cache(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Bio')
        self.assertIsNotNone(cache.get(f'custom_user_info_{self.user.id}'))
        self.assertIsNotNone(cache.get(f'profile_user_info_{self.user.id}'))

    def test_get_profile_view_user_not_found(self):
        url = reverse('account:profile-user', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_profile_view_comments_and_replies_cache(self):
        post = BlogPost.objects.create(
            title_heading="Test Blog Post",
            title_description="Test Description",
            description="This is a test blog post",
        )

        Comment.objects.create(
            content='Test Comment',
            is_approved=False,
            is_reply=False,
            user=self.user,
            post=post
        )

        Comment.objects.create(
            content='Test Reply',
            is_approved=False,
            is_reply=True,
            user=self.user,
            post=post
        )

        self.user.is_staff = True
        self.user.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertIsNotNone(cache.get('approved_comments_in_admin_profile'))
        self.assertIsNotNone(cache.get('approved_reply_in_admin_profile'))

    def test_post_update_profile(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {
            'full_name': 'updated user',
            'bio': 'Updated Bio',
        })
        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.full_name, 'updated user')
        self.assertEqual(self.profile.bio, 'Updated Bio')
        self.assertIsNone(cache.get(f'profile_user_info_{self.user.id}'))

    # def test_post_update_profile_picture(self):
    #     self.client.login(username='testuser', password='testpass')
    #     new_image = SimpleUploadedFile("new_image.jpg", b"new_file_content", content_type="image/jpeg")
    #
    #     response = self.client.post(self.url, {
    #         'photo': new_image,
    #         'bio': 'Updated Bio with Image'
    #     })
    #
    #     self.profile.refresh_from_db()
    #
    #     # self.assertEqual(response.status_code, 302)
    #     self.assertIn('new_image', self.profile.photo.name)
    #     self.assertEqual(self.profile.bio, 'Updated Bio with Image')
    #     self.assertIsNone(cache.get(f'profile_user_info_{self.user.id}'))

    def test_post_invalid_form(self):
        self.client.login(username='testuser', password='testpass')

        response = self.client.post(self.url, {'username': ''})

        self.assertEqual(response.status_code, 200)
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Please correct the errors below.', messages)


class CommentManagementViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = CustomUser.objects.create_user(
            username='user',
            password='testpass',
            full_name='Test User',
            email='user@example.com'

        )
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            is_staff=True
        )

        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

        self.post = BlogPost.objects.create(
            title_heading='Test Post',
            title_description='Description',
            cover_image=cover_image,
            description='Content',
        )

        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content='Test Comment',
        )

        self.reply = Comment.objects.create(
            post=self.post,
            user=self.user,
            content='Test Reply',
            reply=self.comment,
            is_reply=True,
        )

        cache.clear()

        self.url = reverse('account:comment-management', args=[self.comment.id])

    def test_access_by_non_admin(self):
        self.client.login(username='user', password='testpass')
        response = self.client.post(self.url, {'action': 'approve'})
        self.assertRedirects(response, reverse('core:home'))
        self.comment.refresh_from_db()
        self.assertFalse(self.comment.is_approved)

    def test_approve_comment_by_admin(self):
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
        self.client.force_login(self.admin_user)

        cache_key = f"approved_comments_{self.post.id}"
        cache.set(cache_key, 'test_value')

        response = self.client.post(reverse('account:comment-management', args=[self.reply.id]), {'action': 'delete_reply'}, follow=True)

        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=self.reply.id)

        self.assertIsNone(cache.get(cache_key))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Reply deleted successfully.')

