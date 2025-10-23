"""Unit tests of the committee member remove view"""
from django.test import TestCase
from django.urls import reverse
from tsp.tests.helpers import reverse_with_next
from tsp.models import Society, Student
from tsp.forms.society.add_committee_member_form import AddCommitteeMemberForm

class RemoveCommitteeMembersTestCase(TestCase):
    """Unit tests of the committee member remove view"""
    
    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.member = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.url = reverse('remove_committee_member')
        self.form_input = {
            'email': self.member.email,
        }
    
    def test_remove_committee_member_url(self):
        self.assertEqual(self.url, '/remove_committee_member/')

    def test_get_remove_committee_member_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_remove_committee_member_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_remove_committee_member_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
    
    def test_successful_remove_committee_member(self):
        self.client.login(username=self.user.email, password='Password123')
        form = AddCommitteeMemberForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        response = self.client.post('/add_committee_member/', self.form_input, follow=True)
        intial_member_count = self.user.committee_members.count()
        response = self.client.post(self.url, data={'member_pk': self.member.pk}, follow=True) 
        updated_member_count = self.user.committee_members.count()
        self.assertEqual(updated_member_count, intial_member_count-1)   
        self.assertNotIn(self.member, self.user.committee_members)   
        response_url = reverse('list_committee_member')
        self.assertTemplateUsed(response, 'society/committee_members_list.html')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)