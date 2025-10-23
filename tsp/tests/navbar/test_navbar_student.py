"""Unit tests of the student navbar"""
from django.test import TestCase
from django.urls import reverse
from tsp.models import Student

class StudentNavbarTestCase(TestCase): 
    """Unit tests of the student navbar links"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self): 
        self.student = Student.objects.get(email='johndoe@kcl.ac.uk') 
        self.url = reverse('landing')
        
    def test_student_navbar_links(self):
        self.client.login(username=self.student.email, password='Password123')
        response = self.client.get(self.url)
        
        for_you_page_url = reverse('for_you_page')
        self.assertContains(response, for_you_page_url)
        all_events_url = reverse('all_events')
        self.assertContains(response, all_events_url)
        all_societies_url = reverse('all_societies')
        self.assertContains(response, all_societies_url)
        cart_detail_url = reverse('cart_detail')
        self.assertContains(response, cart_detail_url)
        log_out_url = reverse('log_out')
        self.assertContains(response, log_out_url) 
        change_password_url = reverse('change_password')
        self.assertContains(response, change_password_url)
