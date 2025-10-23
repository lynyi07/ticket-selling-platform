"""Unit tests of the society navbar"""
from django.test import TestCase
from django.urls import reverse
from tsp.models import Society

class SocietyNavbarTestCase(TestCase): 
    """Unit tests of the society navbar links"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self): 
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk') 
        self.url = reverse('edit_profile_page')

    def test_society_navbar_links(self):
        self.client.login(username=self.society.email, password='Password123')
        response = self.client.get(self.url)
        edit_profile_page_url = reverse('edit_profile_page')
        self.assertContains(response, edit_profile_page_url)
        events_list_url = reverse('events_list')
        self.assertContains(response, events_list_url)
        create_event_url = reverse('create_event')
        self.assertContains(response, create_event_url)
        list_regular_url = reverse('list_regular_member')
        self.assertContains(response, list_regular_url)
        list_member_url = reverse('list_committee_member')
        self.assertContains(response, list_member_url)
        bank_details_url = reverse('bank_details')
        self.assertContains(response, bank_details_url)
        log_out_url = reverse('log_out')
        self.assertContains(response, log_out_url) 
        change_password_url = reverse('change_password')
        self.assertContains(response, change_password_url)