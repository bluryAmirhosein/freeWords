from django.test import TestCase, RequestFactory, Client
from django.core.cache import cache
from django.urls import reverse
from core.models import BlogPost, Tag, Comment, PostLike
from account.models import ProfileUser, CustomUser
from core.views import HomeView
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from core.forms import PostCreationForm


class HomeViewTest(TestCase):
    """
    Test case for the home view, covering aspects such as status codes,
    pagination, profile context, liked posts, tags, and caching.
    """
    def setUp(self):
        """Set up test data for the home view tests."""
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='password')
        photo = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.profile = ProfileUser.objects.create(user=self.user, bio='Test bio', photo=photo)
        # Create test tags
        self.tag1 = Tag.objects.create(name='Python')
        self.tag2 = Tag.objects.create(name='Django')

        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        # Create test blog posts
        self.post1 = BlogPost.objects.create(
            title_heading='Post 1',
            slug='post-1',
            title_description='Description 1',
            description='Content 1',
            cover_image=cover_image,
        )
        self.post1.tags.add(self.tag1)

        self.post2 = BlogPost.objects.create(
            title_heading='Post 2',
            slug='post-2',
            title_description='Description 2',
            description='Content 2',
            cover_image=cover_image,
        )
        self.post2.tags.add(self.tag2)

        # Create a comment and a like for testing
        Comment.objects.create(post=self.post1, user=self.user, content='Nice post', is_approved=True)
        PostLike.objects.create(post=self.post1, user=self.user)

        cache.clear()

    def test_home_view_status_code(self):
        """Test if home view returns a 200 status code."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_pagination(self):
        """Test if pagination is working correctly (5 posts per page)."""
        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        for i in range(10):
            BlogPost.objects.create(title_heading=f'Post {i}', title_description=f'Desc {i}', description='Content', cover_image=cover_image)
        response = self.client.get(reverse('core:home'))
        self.assertEqual(len(response.context['obj']), 5)

    def test_profile_in_context(self):
        """Test if the logged-in user's profile is included in the context."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.context['profile'], self.profile)

    def test_top_liked_posts(self):
        """Test if the most liked posts are included in the context."""
        response = self.client.get(reverse('core:home'))
        self.assertIn(self.post1, response.context['top_liked_posts'])

    def test_top_tags_posts(self):
        """Test if top tags are included in the context."""
        response = self.client.get(reverse('core:home'))
        self.assertIn(self.tag1, response.context['top_tags_posts'])
        self.assertIn(self.tag2, response.context['top_tags_posts'])

    def test_approved_comments_count(self):
        """Test if the number of approved comments is correctly counted."""
        response = self.client.get(reverse('core:home'))
        post1 = next(post for post in response.context['obj'] if post.id == self.post1.id)
        self.assertEqual(post1.approved_comments, 1)

    def test_cache_top_liked_posts(self):
        """Test if the list of top liked posts is cached."""
        self.client.get(reverse('core:home'))
        cached_data = cache.get('top_liked_posts')
        self.assertIsNotNone(cached_data)
        self.assertIn(self.post1, cached_data)

    def test_cache_profile(self):
        """Test if user profile is cached after login."""
        self.client.login(username='testuser', password='password')
        self.client.get(reverse('core:home'))
        cached_profile = cache.get(f"profile_{self.user.id}")
        self.assertEqual(cached_profile, self.profile)

    def test_profile_not_exist(self):
        """Test if a new user without a profile does not get a profile in the context."""
        new_user = CustomUser.objects.create_user(username='newuser', password='password', email='<test1@email.com>')
        self.client.login(username='newuser', password='password', email='<test@email.com>')
        response = self.client.get(reverse('core:home'))
        self.assertIsNone(response.context['profile'])

    def test_anonymous_user(self):
        """Test if an anonymous user sees the home page without a profile in context."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['profile'])


class BlogPostDetailViewTest(TestCase):
    """
    Test case for the BlogPostDetailView.
    This class tests various aspects of the blog post detail view, including status codes,
    context data, caching mechanisms, and user interactions like commenting and liking posts.
    """
    def setUp(self):
        """Set up test data, including a test user, blog post, and comment."""
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        # Creating a blog post
        self.post = BlogPost.objects.create(title_heading='Test Post', slug='test-post', title_description='Test Desc',
                                            description='Test Content', cover_image=cover_image)
        # Creating a comment on the post
        self.comment = Comment.objects.create(post=self.post, user=self.user, content='Test Comment', is_approved=True)
        # Defining the URL for the post detail view
        self.url = reverse('core:post-detail', args=[self.post.id, self.post.slug])

    def test_post_detail_view_status_code(self):
        """Ensure that the post detail view returns a 200 status code."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_detail_view_context(self):
        """Check if the post and approved comments are present in the context."""
        response = self.client.get(self.url)
        self.assertEqual(response.context['post'], self.post)
        self.assertIn(self.comment, response.context['comments'])

    def test_cache_approved_comments(self):
        """Ensure that approved comments are cached properly."""
        cache_key = f'approved_comments_{self.post.id}'
        cache.set(cache_key, [self.comment], timeout=1200)
        response = self.client.get(self.url)
        self.assertIn(self.comment, response.context['comments'])

    def test_post_new_comment_authenticated(self):
        """Test if an authenticated user can post a new comment."""
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {'new_comment': True, 'content': 'New Comment'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(content='New Comment').exists())
        # Check if success message is displayed
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Your comment will be displayed after it is approved by the administrator.', messages)

    def test_post_new_comment_unauthenticated(self):
        """Ensure an unauthenticated user cannot post a comment."""
        response = self.client.post(self.url, {'new_comment': True, 'content': 'Anonymous Comment'})
        self.assertRedirects(response, f'{self.url}')

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Please login first', messages)

    def test_edit_comment(self):
        """Test if an authenticated user can edit their own comment."""
        self.client.login(username='testuser', password='testpass')

        response = self.client.post(self.url, {
            'edit_comment': True, 'comment_id': self.comment.id, 'content': 'Edited Comment'
        })
        # Refresh the comment from the database and verify changes
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Edited Comment')

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Your comment was successfully edited!', messages)

    def test_top_liked_posts_cache(self):
        """Verify that the most liked posts are cached correctly."""
        popular_post = BlogPost.objects.create(
            title_heading='Popular Post', description='...', slug='popular',
            cover_image=SimpleUploadedFile("test_image.jpg", b"file_content")
        )
        # Simulate likes on the popular post
        for _ in range(5):
            PostLike.objects.get_or_create(user=self.user, post=popular_post)

        cache_key = 'top_liked_posts'

        cache.delete(cache_key)

        response = self.client.get(self.url)

        cached_posts = cache.get(cache_key)
        # Check if cache is correctly set
        self.assertIsNotNone(cached_posts, "Cached posts should not be None")
        self.assertIsInstance(cached_posts, list, "Cached posts should be a list")
        self.assertIn(popular_post, cached_posts, "Popular post should be in cached top liked posts")


class ReplyCommentViewTest(TestCase):
    """
    Test case for testing the reply comment functionality in a blog post.
    This class contains tests for both authenticated and unauthenticated users,
    handling of invalid data, and authorization checks for editing replies.
    """
    def setUp(self):
        """Set up test data, including users, a blog post, and an initial comment."""
        self.user = CustomUser.objects.create_user(username='testuser', password='12345', email='user@email.com')
        self.other_user = CustomUser.objects.create_user(username='otheruser', password='12345',
                                                         email='other_user@email.com')
        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.post = BlogPost.objects.create(title_heading='Test Post', slug='test-post', title_description='desc',
                                            description='Some text', cover_image=cover_image)
        self.comment = Comment.objects.create(post=self.post, user=self.user, content='Test Comment')
        self.client.login(username='testuser', password='12345')
        self.reply_url = reverse('core:reply-comment', args=[self.post.id, self.comment.id])

    def test_create_reply_authenticated(self):
        """Test that an authenticated user can successfully submit a reply to a comment."""
        response = self.client.post(self.reply_url, {
            'content': 'Test Reply'
        })
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Your reply submitted successfully.', messages)
        self.assertTrue(Comment.objects.filter(content='Test Reply').exists())

    def test_create_reply_unauthenticated(self):
        """Test that an unauthenticated user is redirected and cannot post a reply."""
        self.client.logout()
        response = self.client.post(self.reply_url, {
            'content': 'Test Reply'
        })
        self.assertEqual(response.status_code, 302)
        expected_redirect_url = reverse('core:post-detail', args=[self.post.id, self.post.slug])
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Please login first!', messages)
        self.assertRedirects(response, expected_redirect_url)

    def test_create_reply_invalid_form(self):
        """Test that submitting an empty reply form results in an error message."""
        response = self.client.post(self.reply_url, {'content': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)  # No new comment should be created
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Something went wrong!', messages)

    def test_edit_reply_authenticated(self):
        """Test that an authenticated user can edit their own reply successfully."""
        reply = Comment.objects.create(post=self.post, user=self.user, content='Reply to comment',
                                       reply=self.comment, is_reply=True)
        response = self.client.post(self.reply_url, {
            'content': 'Updated Reply',
            'edit_reply': 'True',
            'reply_id': reply.id
        })

        reply.refresh_from_db()
        self.assertEqual(reply.content, 'Updated Reply')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:post-detail', args=[self.post.id, self.post.slug]))

    def test_edit_reply_unauthorized_user(self):
        """Test that a user cannot edit another user's reply."""
        reply = Comment.objects.create(post=self.post, user=self.user, content='Reply to comment', reply=self.comment,
                                       is_reply=True)

        self.client.login(username='otheruser', password='12345')
        response = self.client.post(self.reply_url, {
            'content': 'Unauthorized Edit',
            'edit_reply': 'True',
            'reply_id': reply.id
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:post-detail', args=[self.post.id, self.post.slug]))
        self.assertNotEqual(reply.content, 'Unauthorized Edit')
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("You are not authorized to edit this reply.", messages)

    def test_edit_reply_invalid_data(self):
        """Test that submitting an empty edit reply form does not update the reply content."""
        reply = Comment.objects.create(post=self.post, user=self.user, content='Reply to comment', reply=self.comment, is_reply=True)
        response = self.client.post(self.reply_url, {
            'content': '',
            'edit_reply': 'True',
            'reply_id': reply.id
        })
        reply.refresh_from_db()
        self.assertEqual(reply.content, 'Reply to comment')
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Something went wrong with your reply update.', messages)
        self.assertRedirects(response, reverse('core:post-detail', args=[self.post.id, self.post.slug]))


class DeleteCommentViewTest(TestCase):
    """
    Test case for testing the comment deletion functionality.
    Ensures that only the owner of a comment can delete it, caches are cleared upon deletion,
    success messages are displayed, and proper redirections occur.
    """
    def setUp(self):
        """Set up test data, including users, a blog post, and a comment."""
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='user1', password='testpass', full_name='User One',
                                                   email='user@email.com')
        self.other_user = CustomUser.objects.create_user(username='user2', password='testpass', full_name='User Two',
                                                         email='other_user@email.com')
        self.client.login(username='user1', password='testpass')
        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.post = BlogPost.objects.create(title_heading='Test Post', title_description='Test', slug='test-post',
                                            description='Test content', cover_image=cover_image)
        self.comment = Comment.objects.create(post=self.post, user=self.user, content='Test Comment')
        self.url = reverse('core:delete-comment', args=[self.comment.id])

    def test_delete_comment_by_owner(self):
        """Test that a comment owner can successfully delete their comment."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_cannot_delete_comment_by_other_user(self):
        """Test that another user cannot delete a comment they do not own."""
        self.client.logout()
        self.client.login(username='user2', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_cache_deleted_on_comment_removal(self):
        """Test that the cache for approved comments is cleared when a comment is deleted."""
        cache.set(f"approved_comments_{self.post.id}", 'cached_data')
        self.client.get(self.url)
        self.assertIsNone(cache.get(f"approved_comments_{self.post.id}"))

    def test_success_message_on_comment_deletion(self):
        """Test that a success message is displayed when a comment is deleted."""
        response = self.client.get(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(any(msg.message == 'Your comment has been deleted successfully.' for msg in messages))

    def test_redirect_after_deletion(self):
        """Test that after deleting a comment, the user is redirected to the post detail page."""
        response = self.client.get(self.url)
        expected_url = reverse('core:post-detail', args=[self.post.id, self.post.slug])
        self.assertRedirects(response, expected_url)


class DeleteReplyViewTest(TestCase):
    """
    Test case for testing the reply deletion functionality.
    Ensures that only the owner of a reply can delete it, caches are cleared upon deletion,
    success and error messages are displayed appropriately, and proper redirections occur.
    """
    def setUp(self):
        """Set up test data, including users, a blog post, a comment, and a reply."""
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='user1', password='testpass', full_name='User One',
                                                   email='user@email.com')
        self.other_user = CustomUser.objects.create_user(username='user2', password='testpass', full_name='User Two',
                                                         email='other_user@email.com')
        self.client.login(username='user1', password='testpass')

        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.post = BlogPost.objects.create(title_heading='Test Post', title_description='Test', slug='test-post',
                                            description='Test content', cover_image=cover_image)
        self.comment = Comment.objects.create(post=self.post, user=self.user, content='Test Comment')
        self.reply = Comment.objects.create(post=self.post, user=self.user, content='Test Reply',
                                            reply=self.comment, is_reply=True)
        self.url = reverse('core:delete-reply', args=[self.reply.id])

    def test_delete_reply_by_owner(self):
        """Test that a reply owner can successfully delete their reply."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=self.reply.id).exists())

    def test_cannot_delete_reply_by_other_user(self):
        """Test that another user cannot delete a reply they do not own."""
        self.client.logout()
        self.client.login(username='user2', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(id=self.reply.id).exists())

    def test_cache_deleted_on_reply_removal(self):
        """Test that the cache for approved comments is cleared when a reply is deleted."""
        cache.set(f"approved_comments_{self.post.id}", 'cached_data')
        self.client.get(self.url)
        self.assertIsNone(cache.get(f"approved_comments_{self.post.id}"))

    def test_success_message_on_reply_deletion(self):
        """Test that a success message is displayed when a reply is deleted."""
        response = self.client.get(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(any(msg.message == 'Your reply has been successfully deleted.' for msg in messages))

    def test_error_message_for_unauthorized_user(self):
        """Test that an unauthorized user gets an error message when trying to delete someone else's reply."""
        self.client.logout()
        self.client.login(username='user2', password='testpass')
        response = self.client.get(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(any(msg.message == 'You are not authorized to delete this reply.' for msg in messages))

    def test_redirect_after_deletion(self):
        """Test that after deleting a reply, the user is redirected to the post detail page."""
        response = self.client.get(self.url)
        expected_url = reverse('core:post-detail', args=[self.post.id, self.post.slug])
        self.assertRedirects(response, expected_url)


class LikePostViewTest(TestCase):
    """
    Test case for the like/unlike functionality of blog posts.
    Ensures that only authenticated users can like or unlike a post,
    appropriate messages are displayed, and redirections are handled correctly.
    """
    def setUp(self):
        """Set up test data, including users and a blog post."""
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='user1', password='testpass', full_name='User One',
                                                   email='user@email.com')
        self.other_user = CustomUser.objects.create_user(username='user2', password='testpass', full_name='User Two',
                                                         email='other_user@email.com')
        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.post = BlogPost.objects.create(title_heading='Test Post', title_description='Test', slug='test-post',
                                            description='Test content', cover_image=cover_image)
        self.url = reverse('core:like-post', args=[self.post.pk, self.post.slug])

    def test_redirect_if_not_authenticated(self):
        """Test that unauthenticated users are redirected when trying to like a post."""
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('core:post-detail', args=[self.post.pk, self.post.slug]))

    def test_like_post_by_authenticated_user(self):
        """Test that an authenticated user can successfully like a post."""
        self.client.login(username='user1', password='testpass')
        response = self.client.post(self.url)
        self.assertTrue(PostLike.objects.filter(user=self.user, post=self.post).exists())
        self.assertRedirects(response, reverse('core:post-detail', args=[self.post.pk, self.post.slug]))

    def test_unlike_post_by_authenticated_user(self):
        """Test that an authenticated user can unlike a post they previously liked."""
        self.client.login(username='user1', password='testpass')
        PostLike.objects.create(user=self.user, post=self.post)
        response = self.client.post(self.url)
        self.assertFalse(PostLike.objects.filter(user=self.user, post=self.post).exists())
        self.assertRedirects(response, reverse('core:post-detail', args=[self.post.pk, self.post.slug]))

    def test_like_message_display(self):
        """Test that a success message is displayed when a user likes a post."""
        self.client.login(username='user1', password='testpass')
        response = self.client.post(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(any(msg.message == 'You have liked this post.' for msg in messages))

    def test_unlike_message_display(self):
        """Test that a success message is displayed when a user unlikes a post."""
        self.client.login(username='user1', password='testpass')
        PostLike.objects.create(user=self.user, post=self.post)
        response = self.client.post(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(any(msg.message == 'You have unliked this post.' for msg in messages))


class PostCreationViewTest(TestCase):
    """
    Test case for the creation and updating of blog posts by superusers.
    Ensures that only superusers can create or update posts, validates post data,
    and checks the appropriate responses and redirects.
    """
    def setUp(self):
        """
        Set up the necessary data for the tests, including creating
        a superuser, a normal user, a tag, and an initial blog post.
        """
        self.client = Client()
        self.superuser = CustomUser.objects.create_superuser(
            username='admin', email='admin@test.com', password='password'
        )
        self.user = CustomUser.objects.create_user(
            username='user', email='user@test.com', password='password'
        )
        self.tag = Tag.objects.create(name='Django')
        self.post = BlogPost.objects.create(
            title_heading='Test Post',
            slug='test-post',
            title_description='Test Description',
            description='Test Content'
        )
        self.post.tags.add(self.tag)

    def test_access_denied_for_non_superuser(self):
        """Test that non-superuser users are denied access to the post creation page."""
        self.client.login(username='user', password='password')
        response = self.client.get(reverse('core:post-creation'))
        self.assertNotEqual(response.status_code, 200)

    def test_access_allowed_for_superuser(self):
        """Test that superusers can access the post creation page and see the post creation form."""
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('core:post-creation'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], PostCreationForm)

    def test_create_post_valid_data(self):
        """Test that a superuser can successfully create a new blog post with valid data."""
        self.client.login(username='admin', password='password')
        data = {
            'title_heading': 'New Post',
            'slug': 'new-post',
            'title_description': 'New Description',
            'description': 'New Content',
            'tags': [self.tag.id],
        }
        response = self.client.post(reverse('core:post-creation'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BlogPost.objects.filter(title_heading='New Post').exists())

    def test_update_post_valid_data(self):
        """Test that a superuser can successfully update an existing blog post with valid data."""
        self.client.login(username='admin', password='password')
        data = {
            'title_heading': 'Updated Post',
            'slug': 'test-post',
            'title_description': 'Updated Description',
            'description': 'Updated Content',
            'tags': [self.tag.id],
        }
        response = self.client.post(reverse('core:post-creation', args=[self.post.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.description, 'Updated Content')

    def test_invalid_post_data(self):
        """Test that invalid data submission to the post creation
           page returns an error message and the form is re-rendered.
        """
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('core:post-creation'), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter valid information')
        self.assertIsInstance(response.context['form'], PostCreationForm)
        self.assertTrue(response.context['form'].errors)

    def test_update_nonexistent_post(self):
        """Test that attempting to update a non-existent post results in a 404 error."""
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('core:post-creation', args=[999]))
        self.assertEqual(response.status_code, 404)


class PostsShowViewTests(TestCase):
    """
    Test case for displaying posts, including search functionality,
    post ordering, comment and like counts, and cache behavior.
    """
    def setUp(self):
        """
        Set up the necessary data for the tests, including creating users,
        posts, comments, likes, and clearing the cache.
        """
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')

        self.tag = Tag.objects.create(name='Django')

        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.post1 = BlogPost.objects.create(
            title_heading='Test Post 1',
            title_description='Description 1',
            slug='test-post-1',
            cover_image=cover_image,
        )
        self.post1.tags.add(self.tag)

        self.post2 = BlogPost.objects.create(
            title_heading='Another Post',
            title_description='Another Description',
            slug='another-post',
            cover_image=cover_image,
        )

        Comment.objects.create(post=self.post1, user=self.user, content='Approved Comment', is_approved=True)
        Comment.objects.create(post=self.post1, user=self.user, content='Unapproved Comment', is_approved=False)

        PostLike.objects.create(user=self.user, post=self.post1)

        cache.clear()

    def test_view_status_code(self):
        """Test that the view returns a status code of 200 (OK) when accessed."""
        response = self.client.get(reverse('core:posts'))
        self.assertEqual(response.status_code, 200)

    def test_context_data(self):
        """Test that the context contains the correct data,
         specifically checking for the 'obj' and 'query' variables in the context.
        """
        response = self.client.get(reverse('core:posts'))
        self.assertIn('obj', response.context)
        self.assertIn('query', response.context)

    def test_post_ordering(self):
        """
        Test that the posts are ordered correctly, with the most recent
        post appearing first (by the post date or other ordering logic).
        """
        response = self.client.get(reverse('core:posts'))
        posts = response.context['obj']
        self.assertEqual(posts[0], self.post2)

    def test_search_functionality(self):
        """
        Test that the search functionality works correctly, returning only
        posts that match the search query.
        """
        response = self.client.get(reverse('core:posts'), {'q': 'Test'})
        self.assertContains(response, 'Test Post 1')
        self.assertNotContains(response, 'Another Post')

    def test_comment_and_like_count(self):
        """
        Test that the comment and like counts for a post are correctly
        reflected in the context.
        """
        response = self.client.get(reverse('core:posts'))
        post1 = next(post for post in response.context['obj'] if post.id == self.post1.id)
        self.assertEqual(post1.approved_comments, 1)
        self.assertEqual(post1.like_count, 1)

    def test_cache_behavior(self):
        """
        Test that the cache is populated with the correct data when
        the posts page is accessed.
        """
        self.client.get(reverse('core:posts'))
        cache_data = cache.get('approved_comments')
        self.assertIsNotNone(cache_data)

    def test_all_posts_are_displayed(self):
        """
        Test that all posts are displayed on the posts page, ensuring that
        both `Test Post 1` and `Another Post` are included in the response.
        """
        response = self.client.get(reverse('core:posts'))
        self.assertContains(response, 'Test Post 1')
        self.assertContains(response, 'Another Post')


class DeletePostViewTest(TestCase):
    """
    Test case for deleting a post, ensuring that only superusers can delete posts
    and checking the behavior when deleting a post or a non-existent post.
    """
    def setUp(self):
        """
        Set up the necessary data for the tests, including creating users, a post,
        and defining the URL for deleting the post.
        """
        self.superuser = CustomUser.objects.create_superuser(username='admin', email='admin@test.com', password='adminpass')
        self.normal_user = CustomUser.objects.create_user(username='user', email='user@test.com', password='userpass')
        self.post = BlogPost.objects.create(title_heading='Test Post', title_description='Description',
                                            description='Content')

        self.delete_url = reverse('core:delete', args=[self.post.pk])

    def test_only_superuser_can_delete_post(self):
        """Test that only superusers can delete a post. Normal users should get a 403 Forbidden response."""
        self.client.login(username='user', password='userpass')
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_delete_post(self):
        """
        Test that a superuser can successfully delete a post. The post should be removed from the database,
        and a success message should be displayed.
        """
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.delete_url, follow=True)
        self.assertRedirects(response, reverse('core:posts'))
        self.assertFalse(BlogPost.objects.filter(pk=self.post.pk).exists())
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The post was deleted successfully.")

    def test_redirect_after_deletion(self):
        """Test that after a successful post deletion, the user is redirected to the list of posts."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.delete_url)
        self.assertRedirects(response, reverse('core:posts'))

    def test_deleting_nonexistent_post_returns_404(self):
        """Test that attempting to delete a non-existent post returns a 404 status code."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("core:delete", args=[9999]))
        self.assertEqual(response.status_code, 404)
