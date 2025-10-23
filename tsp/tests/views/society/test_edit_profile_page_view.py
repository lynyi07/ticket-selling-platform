"""Unit tests of the edit profile page view for a society account"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, Event

class EditProfileViewTestCase(TestCase):
    """Unit tests of the edit profile page view for a society account"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json'
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.event = Event.objects.get(name='Default test event')
        self.url = reverse('edit_profile_page')
    
    def test_request_url(self):
        self.assertEqual(self.url, '/edit_profile_page/')

    def test_get_request(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'society/edit_profile_page.html')

    def test_get_edit_profile_page_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_edit_profile_page_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_edit_profile_page_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
    
    def test_button_links_present(self):
        #these links should only be present for a society account
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        list_follower_url = reverse('list_follower')
        self.assertContains(response, list_follower_url)
        list_regular_member_url = reverse('list_regular_member')
        self.assertContains(response, list_regular_member_url)
        member_discount_url = reverse('member_discount')
        self.assertContains(response, member_discount_url)
        list_subscriber_url = reverse('list_subscriber')
        self.assertContains(response, list_subscriber_url)
        events_list_url = reverse('events_list')
        self.assertContains(response, events_list_url)
        list_committee_member_url = reverse('list_committee_member')
        self.assertContains(response, list_committee_member_url)
    
    def test_template_content_headings(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)     
        self.assertContains(response, self.user.name)        
        self.assertContains(response, self.user.email)