from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )

    def test_registration_succeeds(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_registration_rejects_password_mismatch(self):
        response = self.client.post(reverse('signup'), {
            'username': 'mismatchuser',
            'email': 'mismatch@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'DifferentPassword456!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatchuser').exists())

    def test_registration_rejects_duplicate_username(self):
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        })
        self.assertEqual(response.status_code, 200)

    def test_login_with_username_succeeds(self):
        response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'TestPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_login_with_email_succeeds(self):
        response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser@example.com',
            'password': 'TestPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_login_with_invalid_credentials_rejected(self):
        response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'WrongPassword999'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username/email or password")

    def test_logout_works_with_post(self):
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        # Check that user is logged out
        profile_response = self.client.get(reverse('profile'))
        self.assertEqual(profile_response.status_code, 302)

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
