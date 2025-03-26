from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import CustomUser, BlogPost, Tag, PostLike, Comment
from account.models import CustomUser, ProfileUser


class BlogModelsTest(TestCase):
    """
    This test case includes tests for models like Tag, BlogPost, Comment, and PostLike.
    It verifies the creation of these models, their relationships, and important methods.
    """
    def setUp(self):
        """
        This method is used to set up the test environment.
        It creates a user, tag, blog post, comment, and like that will be used in the tests.
        """
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
        """Test that a tag is created correctly and stored in the database."""
        self.assertEqual(self.tag.name, "Django")
        self.assertEqual(Tag.objects.count(), 1)

    def test_blogpost_creation(self):
        """Test that a blog post is created correctly and associated with tags."""
        self.assertEqual(self.post.title_heading, "Test Post")
        self.assertIn(self.tag, self.post.tags.all())  # Ensure that the tag is associated with the post

    def test_blogpost_get_absolute_url(self):
        """Test the `get_absolute_url` method of BlogPost to ensure it returns the correct URL."""
        self.assertEqual(self.post.get_absolute_url(), f"/post-detail/{self.post.id}/{self.post.slug}/")

    def test_comment_creation(self):
        """Test the creation of a comment and ensure it is associated with the correct post and user."""
        self.assertEqual(self.comment.content, "Nice post!")
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.user, self.user)

    def test_comment_replies(self):
        """Test the creation of a reply to a comment and ensure the reply is linked correctly."""
        # Create a reply to the existing comment
        reply = Comment.objects.create(post=self.post, user=self.user, content="Thanks!", reply=self.comment,
                                       is_reply=True)
        self.assertEqual(reply.reply, self.comment)
        self.assertTrue(reply.is_reply)

    def test_post_like(self):
        """Test that a like is created correctly and associated with the correct post and user."""
        self.assertEqual(self.like.user, self.user)
        self.assertEqual(self.like.post, self.post)

    def test_unique_post_like(self):
        """Test that a user can only like a post once. This ensures uniqueness of post likes."""
        with self.assertRaises(Exception):  # Ensure that attempting to like the same post twice raises an exception
            PostLike.objects.create(user=self.user, post=self.post)