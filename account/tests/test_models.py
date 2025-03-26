from django.test import TestCase
from account.models import CustomUser, ProfileUser


class CustomUserModelTest(TestCase):
    """
    This test case includes tests for the CustomUser model.
    It verifies the creation of a user, the uniqueness of the email and username,
    and the proper functioning of the `__str__` method and password verification.
    """
    def setUp(self):
        """This method sets up the environment for testing. It creates a user that will be used in the tests."""
        self.user = CustomUser.objects.create_user(
            full_name="Test User",
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )

    def test_user_creation(self):
        """
        Test that a user is created correctly and all fields are properly set.
        Verifies the full name, email, username, and password.
        """
        self.assertEqual(self.user.full_name, "Test User")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(self.user.check_password("testpassword123"))

    def test_user_str_method(self):
        """
        Test the `__str__` method of the CustomUser model.
        It should return the username of the user when the user object is converted to a string.
        """
        self.assertEqual(str(self.user), "testuser")

    def test_unique_email(self):
        """
        Test that the email field is unique.
        Attempts to create a new user with a duplicate email should raise an exception.
        """
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(
                full_name="Another User",
                email="test@example.com",  # Duplicate email
                username="anotheruser",
                password="anotherpassword"
            )

    def test_unique_username(self):
        """
        Test that the username field is unique.
        Attempts to create a new user with a duplicate username should raise an exception.
        """
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(
                full_name="Another User",
                email="another@example.com",
                username="testuser",  # Duplicate username
                password="anotherpassword"
            )


class ProfileUserModelTest(TestCase):
    """
    This test case includes tests for the ProfileUser model.
    It verifies the creation of a profile, the relationship with the user,
    and the proper functioning of the `__str__` method.
    """
    def setUp(self):
        """This method sets up the environment for testing. It creates a user and a profile for that user."""
        self.user = CustomUser.objects.create_user(
            full_name="Test User",
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        self.profile = ProfileUser.objects.create(
            user=self.user,
            bio="This is a test bio"
        )

    def test_profile_creation(self):
        """
        Test that a profile is created correctly and that the relationship with the user works.
        Verifies that the profile's user and bio are set correctly.
        """
        self.assertEqual(self.profile.user.username, "testuser")  # Ensure the profile is related to the correct user
        self.assertEqual(self.profile.bio, "This is a test bio")

    def test_profile_str_method(self):
        """
        Test the `__str__` method of the ProfileUser model.
        It should return the username of the associated user when the profile object is converted to a string.
        """
        self.assertEqual(str(self.profile), "testuser")

    def test_profile_user_relation(self):
        """
        Test the relationship between the ProfileUser model and the CustomUser model.
        Ensures that a user can access their associated profile via the `profile` related name.
        """
        self.assertEqual(self.user.profile.first(), self.profile)  # Ensure the user has the correct profile associated with them
