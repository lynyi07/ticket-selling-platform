"""Unit tests of log out view"""
from django.test import TestCase
from django.urls import reverse
from ..helpers import LoginTester
from tsp.tests.helpers import reverse_with_next

class LogOutViewTestCase(TestCase, LoginTester):
    """Unit tests of log out view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self):
        self.url = reverse('log_out')

    def test_log_out_url(self):
        self.assertEqual(self.url, '/log_out/')

    def test_get_log_out(self):
        self.client.login(email = 'johndoe@kcl.ac.uk', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('landing')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
        self.assertFalse(self._is_logged_in())

    def test_get_log_out_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        response_url = reverse_with_next('login', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertFalse(self._is_logged_in())