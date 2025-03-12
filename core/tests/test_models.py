from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import CustomUser, BlogPost, Tag, PostLike, Comment
from account.models import CustomUser, ProfileUser


class BlogModelsTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="testpass")
        self.tag = Tag.objects.create(name="Django")
        self.post = BlogPost.objects.create(
            title_heading="Test Post",
            title_description="Test Description",
            description="Test Content",
        )
        self.post.tags.add(self.tag)
        self.comment = Comment.objects.create(post=self.post, user=self.user, content="Nice post!")
        self.like = PostLike.objects.create(user=self.user, post=self.post)

    def test_tag_creation(self):
        self.assertEqual(self.tag.name, "Django")
        self.assertEqual(Tag.objects.count(), 1)

    def test_blogpost_creation(self):
        self.assertEqual(self.post.title_heading, "Test Post")
        self.assertIn(self.tag, self.post.tags.all())

    def test_blogpost_get_absolute_url(self):
        self.assertEqual(self.post.get_absolute_url(), f"/post-detail/{self.post.id}/{self.post.slug}/")

    def test_comment_creation(self):
        self.assertEqual(self.comment.content, "Nice post!")
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.user, self.user)

    def test_comment_replies(self):
        reply = Comment.objects.create(post=self.post, user=self.user, content="Thanks!", reply=self.comment,
                                       is_reply=True)
        self.assertEqual(reply.reply, self.comment)
        self.assertTrue(reply.is_reply)

    def test_post_like(self):
        self.assertEqual(self.like.user, self.user)
        self.assertEqual(self.like.post, self.post)

    def test_unique_post_like(self):
        with self.assertRaises(Exception):
            PostLike.objects.create(user=self.user, post=self.post)