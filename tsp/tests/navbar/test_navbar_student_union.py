"""Unit tests of the student union navbar"""
from django.test import TestCase
from django.urls import reverse
from tsp.models import StudentUnion

class StudentUnionNavbarTestCase(TestCase): 
    """Unit tests of the student union navbar links"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self): 
        self.student = StudentUnion.objects.get(email='kclsu@kcl.ac.uk') 
        self.url = reverse('landing')
        
    def test_student_union_navbar_links(self):
        self.client.login(username=self.student.email, password='Password123')
        response = self.client.get(self.url)
        
        view_societies_url = reverse('view_societies')
        self.assertContains(response, view_societies_url)
        create_society_url = reverse('create_society')
        self.assertContains(response, create_society_url)
        log_out_url = reverse('log_out')
        self.assertContains(response, log_out_url) 
        change_password_url = reverse('change_password')
        self.assertContains(response, change_password_url)