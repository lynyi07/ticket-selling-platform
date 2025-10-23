"""Unit tests of landing page view"""
from django.test import TestCase
from django.urls import reverse
from ..helpers import LoginTester

class LandingPageViewTestCase(TestCase, LoginTester):
    """Unit tests of landing page view"""

    fixtures = [
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.url = reverse('landing')

    def test_url(self):
        self.assertEqual(self.url, '/')

    def test_get_landing_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')   # Check whether correct template has been used