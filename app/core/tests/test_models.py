from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_email_succesful(self):
        """Test creating a new user with an email is succesful"""
        email = 'test@email.com'
        password = 'pass'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """TEst the email for a new user is normalized"""

        email = 'test@AEMAIL.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'password')

    def test_create_new_super_user(self):
        """Test creating a new superuser"""

        user = get_user_model().objects. \
            create_superuser('email@email.com', '123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)