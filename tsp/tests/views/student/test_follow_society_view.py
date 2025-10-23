"""Unit tests of the follow society view for a student account"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, Student

class FollowSocietyViewTestCase(TestCase):
    """Unit tests of the follow society view for a student account"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json'
    ]

    def setUp(self):
        self.user = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk') 
        self.url = reverse('follow_society')
    
    def test_url(self):
        self.assertEqual(self.url, '/follow_society/')
        
    def test_successful_follow_society(self):
        self.client.login(username=self.user.email, password='Password123')
        before_count = self.society.follower.count()
        response = self.client.post(self.url, {'society_pk': self.society.pk}, follow=True)
        response_url = reverse('society_page',  kwargs={'pk': self.society.pk})
        self.assertRedirects(response, response_url, 302, 200)
        after_count = self.society.follower.count()
        self.assertEqual(before_count+1, after_count)
        
    def test_successful_unfollow_society(self):
        self.society.add_follower(self.user)
        self.client.login(username=self.user.email, password='Password123')
        before_count = self.society.follower.count()
        response = self.client.post(self.url, {'society_pk': self.society.pk}, follow=True)
        response_url = reverse('society_page',  kwargs={'pk': self.society.pk})
        self.assertRedirects(response, response_url, 302, 200)
        after_count = self.society.follower.count()
        self.assertEqual(before_count-1, after_count)

    def test_get_follow_society_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_follow_society_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_follow_society_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
