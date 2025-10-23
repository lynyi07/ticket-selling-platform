"""Unit tests of the view society profile view for a student union account"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, StudentUnion

class SocietyProfileViewTestCase(TestCase):
    """Unit tests of the view society profile view for a student union account"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json'
    ]

    def setUp(self):
        self.user = StudentUnion.objects.get(email='kclsu@kcl.ac.uk')
        self.other_user = StudentUnion.objects.get(email='qmusu@qmw.ac.uk')
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.url = reverse('society_profile', kwargs={'pk': self.society.id})
    
    def test_request_url(self):
        self.assertEqual(self.url, '/society_profile/' + str(self.society.id) + '/')

    def test_get_request(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_union/society_profile_page.html')

    def test_get_society_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        
    def test_get_society_profile_returns_404_when_access_society_in_other_university(self):
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_get_society_profile_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_society_profile_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
    
    def test_button_links_not_present(self):
        #these links should not be present for a student union account
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        list_follower_url = reverse('list_follower')
        self.assertNotContains(response, list_follower_url)
        list_regular_member_url = reverse('list_regular_member')
        self.assertNotContains(response, list_regular_member_url)
        member_discount_url = reverse('member_discount')
        self.assertNotContains(response, member_discount_url)
        list_subscriber_url = reverse('list_subscriber')
        self.assertNotContains(response, list_subscriber_url)
        events_list_url = reverse('events_list')
        self.assertNotContains(response, events_list_url)
        list_committee_member_url = reverse('list_committee_member')
        self.assertNotContains(response, list_committee_member_url)

    def test_template_content_headings(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)     
        self.assertContains(response, self.society.name)        
        self.assertContains(response, self.society.email)