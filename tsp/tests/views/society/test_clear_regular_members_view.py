"""Unit tests of the clear regular members view"""
from django.test import TestCase
from tsp.models import Society, Student
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse

class ClearRegularMembersViewTestCase(TestCase):
    """Unit tests of the clear regular members view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json'
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self._set_up_regular_members()
        self.url = reverse('clear_regular_members')

    def _set_up_regular_members(self):
        member_first = Student.objects.get(email='johndoe@kcl.ac.uk')
        member_second = Student.objects.get(email='janedoe@kcl.ac.uk')
        self.user.add_regular_member(member_first)
        self.user.add_regular_member(member_second)
    
    def test_clear_regular_members_url(self):
        self.assertEqual(self.url, f'/clear_regular_members/') 

    def test_get_clear_regular_members_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_clear_regular_members_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_clear_regular_members_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
    
    def test_successful_clear_regular_members(self):
        members_count_before = self.user.regular_members.count()
        self.assertNotEqual(members_count_before, 0)
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.post(self.url, follow=True)
        # Test if all regular members are removed.
        members_count_after = self.user.regular_members.count()
        self.assertEqual(members_count_after, 0)
        # Test the success message and the redirected page.
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "All regular members have been removed.")
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('list_regular_member'))