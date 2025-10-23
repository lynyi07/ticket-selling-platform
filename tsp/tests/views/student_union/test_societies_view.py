"""Unit tests of the view societies view"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, StudentUnion

class SocietiesViewTestCase(TestCase):
    """Unit tests of the view societies view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
    ]

    def setUp(self):
        self.user = StudentUnion.objects.get(email='kclsu@kcl.ac.uk')
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.url = reverse('view_societies')

    def test_url(self):
        self.assertEqual(self.url, '/view_societies/')

    def test_get_view_societies(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_societies(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_union/societies_list.html')
        self.assertEqual(len(response.context['object_list']), 15)
        for society_id in range(15-1):
            self.assertContains(response, f'society.{society_id}@kcl.ac.uk')
            self.assertContains(response, f'KCL society.{society_id}')
            self.assertContains(response, f'{society_id + 1}')
        
    def test_get_view_societies_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_view_societies_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_view_societies_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def _create_test_societies(self, society_count=10):
        for society_id in range(society_count):
            Society.objects.create_user(
                email = f'society.{society_id}@kcl.ac.uk',
                password = 'Password123',
                student_union = self.user,
                name = f'KCL society.{society_id}',
                member_discount = 5,
                university = self.user.university,
                role = 'SOCIETY',
                is_superuser = False
            )
            
    def test_template_content_headings(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)     
        self.assertContains(response, "List of Societies in KCL Student Union")        
    
    def test_button_links_present(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        create_society_url = reverse('create_society')
        self.assertContains(response, create_society_url)
        society_profile_url = reverse('society_profile', kwargs={'pk':self.society.pk})
        self.assertContains(response, society_profile_url)