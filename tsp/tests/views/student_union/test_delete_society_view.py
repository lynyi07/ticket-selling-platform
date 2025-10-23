"""Unit tests of the delete society view"""
from django.test import TestCase
from django.urls import reverse
from tsp.tests.helpers import reverse_with_next
from tsp.models import Society, StudentUnion

class DeleteSocietyViewTestCase(TestCase):
    """Unit tests of the delete society view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self):
        self.user = StudentUnion.objects.get(email='kclsu@kcl.ac.uk')
        self.Society = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.url = reverse('delete_society')
    
    def test_delete_society_url(self):
        self.assertEqual(self.url, f'/delete_society/')
    
    def test_get_delete_society(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = Society.objects.count()
        response = self.client.post(self.url, {'society_id': self.Society.id}, follow=True)
        after_count = Society.objects.count()
        self.assertEqual(before_count - 1, after_count)
        redirect_url = reverse('view_societies')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
    
    def test_unsuccessful_delete_society_with_non_existing_society_id(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = Society.objects.count()
        response = self.client.post(self.url, {'society_id': 10000000000}, follow=True)
        after_count = Society.objects.count()
        self.assertEqual(before_count, after_count)
        redirect_url = reverse('view_societies')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_get_delete_society_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_delete_society_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_delete_society_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')