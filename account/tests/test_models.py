from django.test import TestCase
from account.models import CustomUser, ProfileUser


# class CustomUserModelTest(TestCase):
#     def setUp(self):
#         self.user = CustomUser.objects.create_user(
#             full_name="Test User",
#             email="test@example.com",
#             username="testuser",
#             password="testpassword123"
#         )
#
#     def test_user_creation(self):
#         self.assertEqual(self.user.full_name, "Test User")
#         self.assertEqual(self.user.email, "test@example.com")
#         self.assertEqual(self.user.username, "testuser")
#         self.assertTrue(self.user.check_password("testpassword123"))
#
#     def test_user_str_method(self):
#         self.assertEqual(str(self.user), "testuser")
#
#     def test_unique_email(self):
#         with self.assertRaises(Exception):
#             CustomUser.objects.create_user(
#                 full_name="Another User",
#                 email="test@example.com",  # Duplicate email
#                 username="anotheruser",
#                 password="anotherpassword"
#             )
#
#     def test_unique_username(self):
#         with self.assertRaises(Exception):
#             CustomUser.objects.create_user(
#                 full_name="Another User",
#                 email="another@example.com",
#                 username="testuser",  # Duplicate username
#                 password="anotherpassword"
#             )
#
#
# class ProfileUserModelTest(TestCase):
#     def setUp(self):
#         self.user = CustomUser.objects.create_user(
#             full_name="Test User",
#             email="test@example.com",
#             username="testuser",
#             password="testpassword123"
#         )
#         self.profile = ProfileUser.objects.create(
#             user=self.user,
#             bio="This is a test bio"
#         )
#
#     def test_profile_creation(self):
#         self.assertEqual(self.profile.user.username, "testuser")
#         self.assertEqual(self.profile.bio, "This is a test bio")
#
#     def test_profile_str_method(self):
#         self.assertEqual(str(self.profile), "testuser")
#
#     def test_profile_user_relation(self):
#         self.assertEqual(self.user.profile.first(), self.profile)
