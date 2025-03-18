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
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='password')
        photo = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.profile = ProfileUser.objects.create(user=self.user, bio='Test bio', photo=photo)

        self.tag1 = Tag.objects.create(name='Python')
        self.tag2 = Tag.objects.create(name='Django')

        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

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

        Comment.objects.create(post=self.post1, user=self.user, content='Nice post', is_approved=True)
        PostLike.objects.create(post=self.post1, user=self.user)

        cache.clear()

    def test_home_view_status_code(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_pagination(self):
        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        for i in range(10):
            BlogPost.objects.create(title_heading=f'Post {i}', title_description=f'Desc {i}', description='Content', cover_image=cover_image)
        response = self.client.get(reverse('core:home'))
        self.assertEqual(len(response.context['obj']), 5)


    def test_profile_in_context(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.context['profile'], self.profile)

    def test_top_liked_posts(self):
        response = self.client.get(reverse('core:home'))
        self.assertIn(self.post1, response.context['top_liked_posts'])

    def test_top_tags_posts(self):
        response = self.client.get(reverse('core:home'))
        self.assertIn(self.tag1, response.context['top_tags_posts'])
        self.assertIn(self.tag2, response.context['top_tags_posts'])


    def test_approved_comments_count(self):
        response = self.client.get(reverse('core:home'))
        post1 = next(post for post in response.context['obj'] if post.id == self.post1.id)
        self.assertEqual(post1.approved_comments, 1)

    def test_cache_top_liked_posts(self):
        self.client.get(reverse('core:home'))
        cached_data = cache.get('top_liked_posts')
        self.assertIsNotNone(cached_data)
        self.assertIn(self.post1, cached_data)

    def test_cache_profile(self):
        self.client.login(username='testuser', password='password')
        self.client.get(reverse('core:home'))
        cached_profile = cache.get(f"profile_{self.user.id}")
        self.assertEqual(cached_profile, self.profile)

    def test_profile_not_exist(self):
        new_user = CustomUser.objects.create_user(username='newuser', password='password', email='<test1@email.com>')
        self.client.login(username='newuser', password='password', email='<test@email.com>')
        response = self.client.get(reverse('core:home'))
        self.assertIsNone(response.context['profile'])

    def test_anonymous_user(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['profile'])


class BlogPostDetailViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        cover_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.post = BlogPost.objects.create(
            title_heading='Test Post', slug='test-post', title_description='Test Desc', description='Test Content',
            cover_image=cover_image
        )
        self.comment = Comment.objects.create(
            post=self.post, user=self.user, content='Test Comment', is_approved=True
        )
        self.url = reverse('core:post-detail', args=[self.post.id, self.post.slug])

    def test_post_detail_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_detail_view_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['post'], self.post)
        self.assertIn(self.comment, response.context['comments'])

    def test_cache_approved_comments(self):
        cache_key = f'approved_comments_{self.post.id}'
        cache.set(cache_key, [self.comment], timeout=1200)
        response = self.client.get(self.url)
        self.assertIn(self.comment, response.context['comments'])

    def test_post_new_comment_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {'new_comment': True, 'content': 'New Comment'})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(content='New Comment').exists())

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Your comment will be displayed after it is approved by the administrator.', messages)

    def test_post_new_comment_unauthenticated(self):
        response = self.client.post(self.url, {'new_comment': True, 'content': 'Anonymous Comment'})
        self.assertRedirects(response, f'{self.url}')

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Please login first', messages)

    def test_edit_comment(self):
        self.client.login(username='testuser', password='testpass')

        response = self.client.post(self.url, {
            'edit_comment': True, 'comment_id': self.comment.id, 'content': 'Edited Comment'
        })

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Edited Comment')

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('your comment was successfully edit!', messages)

    def test_top_liked_posts_cache(self):
        popular_post = BlogPost.objects.create(
            title_heading='Popular Post', description='...', slug='popular',
            cover_image=SimpleUploadedFile("test_image.jpg", b"file_content")
        )

        for _ in range(5):
            PostLike.objects.get_or_create(user=self.user, post=popular_post)

        cache_key = 'top_liked_posts'

        cache.delete(cache_key)

        response = self.client.get(self.url)

        cached_posts = cache.get(cache_key)

        self.assertIsNotNone(cached_posts, "Cached posts should not be None")
        self.assertIsInstance(cached_posts, list, "Cached posts should be a list")
        self.assertIn(popular_post, cached_posts, "Popular post should be in cached top liked posts")

class ReplyCommentViewTest(TestCase):
    def setUp(self):
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
        response = self.client.post(self.reply_url, {
            'content': 'Test Reply'
        })
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Your reply submitted successfully.', messages)
        self.assertTrue(Comment.objects.filter(content='Test Reply').exists())

    def test_create_reply_unauthenticated(self):
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
        response = self.client.post(self.reply_url, {'content': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Something went wrong!', messages)

    def test_edit_reply_authenticated(self):
        reply = Comment.objects.create(post=self.post, user=self.user, content='Reply to comment', reply=self.comment,
                                       is_reply=True)

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
    def setUp(self):
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
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_cannot_delete_comment_by_other_user(self):
        self.client.logout()
        self.client.login(username='user2', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_cache_deleted_on_comment_removal(self):
        cache.set(f"approved_comments_{self.post.id}", 'cached_data')
        self.client.get(self.url)
        self.assertIsNone(cache.get(f"approved_comments_{self.post.id}"))

    def test_success_message_on_comment_deletion(self):
        response = self.client.get(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(any(msg.message == 'Your comment has been deleted successfully.' for msg in messages))

    def test_redirect_after_deletion(self):
        response = self.client.get(self.url)
        expected_url = reverse('core:post-detail', args=[self.post.id, self.post.slug])
        self.assertRedirects(response, expected_url)


class DeleteReplyViewTest(TestCase):
    def setUp(self):
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
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=self.reply.id).exists())

    def test_cannot_delete_reply_by_other_user(self):
        self.client.logout()
        self.client.login(username='user2', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(id=self.reply.id).exists())

    def test_cache_deleted_on_reply_removal(self):
        cache.set(f"approved_comments_{self.post.id}", 'cached_data')
        self.client.get(self.url)
        self.assertIsNone(cache.get(f"approved_comments_{self.post.id}"))

    def test_success_message_on_reply_deletion(self):
        response = self.client.get(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(any(msg.message == 'Your reply has been successfully deleted.' for msg in messages))

    def test_error_message_for_unauthorized_user(self):
        self.client.logout()
        self.client.login(username='user2', password='testpass')
        response = self.client.get(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(any(msg.message == 'You are not authorized to delete this reply.' for msg in messages))

    def test_redirect_after_deletion(self):
        response = self.client.get(self.url)
        expected_url = reverse('core:post-detail', args=[self.post.id, self.post.slug])
        self.assertRedirects(response, expected_url)


class LikePostViewTest(TestCase):
    def setUp(self):
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
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('core:post-detail', args=[self.post.pk, self.post.slug]))

    def test_like_post_by_authenticated_user(self):
        self.client.login(username='user1', password='testpass')
        response = self.client.post(self.url)
        self.assertTrue(PostLike.objects.filter(user=self.user, post=self.post).exists())
        self.assertRedirects(response, reverse('core:post-detail', args=[self.post.pk, self.post.slug]))

    def test_unlike_post_by_authenticated_user(self):
        self.client.login(username='user1', password='testpass')
        PostLike.objects.create(user=self.user, post=self.post)
        response = self.client.post(self.url)
        self.assertFalse(PostLike.objects.filter(user=self.user, post=self.post).exists())
        self.assertRedirects(response, reverse('core:post-detail', args=[self.post.pk, self.post.slug]))

    def test_like_message_display(self):
        self.client.login(username='user1', password='testpass')
        response = self.client.post(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(any(msg.message == 'You have liked this post.' for msg in messages))

    def test_unlike_message_display(self):
        self.client.login(username='user1', password='testpass')
        PostLike.objects.create(user=self.user, post=self.post)
        response = self.client.post(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(any(msg.message == 'You have unliked this post.' for msg in messages))


class PostCreationViewTest(TestCase):
    def setUp(self):
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
        self.client.login(username='user', password='password')
        response = self.client.get(reverse('core:post-creation'))
        self.assertNotEqual(response.status_code, 200)

    def test_access_allowed_for_superuser(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('core:post-creation'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], PostCreationForm)

    def test_create_post_valid_data(self):
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
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('core:post-creation'), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please Enter valid information')
        self.assertIsInstance(response.context['form'], PostCreationForm)
        self.assertTrue(response.context['form'].errors)

    def test_update_nonexistent_post(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('core:post-creation', args=[999]))
        self.assertEqual(response.status_code, 404)


class PostsShowViewTests(TestCase):
    def setUp(self):
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
        response = self.client.get(reverse('core:posts'))
        self.assertEqual(response.status_code, 200)

    def test_context_data(self):
        response = self.client.get(reverse('core:posts'))
        self.assertIn('obj', response.context)
        self.assertIn('query', response.context)

    def test_post_ordering(self):
        response = self.client.get(reverse('core:posts'))
        posts = response.context['obj']
        self.assertEqual(posts[0], self.post2)

    def test_search_functionality(self):
        response = self.client.get(reverse('core:posts'), {'q': 'Test'})
        self.assertContains(response, 'Test Post 1')
        self.assertNotContains(response, 'Another Post')

    def test_comment_and_like_count(self):
        response = self.client.get(reverse('core:posts'))
        post1 = next(post for post in response.context['obj'] if post.id == self.post1.id)
        self.assertEqual(post1.approved_comments, 1)
        self.assertEqual(post1.like_count, 1)

    def test_cache_behavior(self):
        self.client.get(reverse('core:posts'))
        cache_data = cache.get('approved_comments')
        self.assertIsNotNone(cache_data)

    def test_all_posts_are_displayed(self):
        response = self.client.get(reverse('core:posts'))
        self.assertContains(response, 'Test Post 1')
        self.assertContains(response, 'Another Post')


class DeletePostViewTest(TestCase):
    def setUp(self):
        self.superuser = CustomUser.objects.create_superuser(username='admin', email='admin@test.com', password='adminpass')
        self.normal_user = CustomUser.objects.create_user(username='user', email='user@test.com', password='userpass')
        self.post = BlogPost.objects.create(title_heading='Test Post', title_description='Description',
                                            description='Content')

        self.delete_url = reverse('core:delete', args=[self.post.pk])

    def test_only_superuser_can_delete_post(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_delete_post(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.delete_url, follow=True)
        self.assertRedirects(response, reverse('core:posts'))
        self.assertFalse(BlogPost.objects.filter(pk=self.post.pk).exists())
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The post was deleted successfully.")

    def test_redirect_after_deletion(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.delete_url)
        self.assertRedirects(response, reverse('core:posts'))

    def test_deleting_nonexistent_post_returns_404(self):
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("core:delete", args=[9999]))
        self.assertEqual(response.status_code, 404)
