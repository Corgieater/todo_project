from django.test import TestCase
from users.models import CustomUser


class TestCustomUser(TestCase):
    def test_create_valid_user(self):
        user = CustomUser.objects.create_superuser(
            email="user@example.com",
            name="user",
            password="abcd4321",
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.email, "user@example.com")
        self.assertTrue(user.check_password("abcd4321"))

    def test_create_user_without_email_error(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email=None, password="test123")

    def test_create_superuser(self):
        admin_user = CustomUser.objects.create_superuser(
            email="admin@example.com", name="Admin User", password="adminpassword123"
        )
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
