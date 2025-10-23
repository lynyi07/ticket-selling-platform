"""Unit tests of the committee member add view"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, Student
from tsp.forms.society.add_committee_member_form import AddCommitteeMemberForm

class AddCommitteeMembersTestCase(TestCase):
    """Unit tests of the committee member add view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.url = reverse('add_committee_member')
        self.form_input = {
            'email': 'johndoe@kcl.ac.uk',
        }

    def test_get_request(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'society/committee_member_add.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, AddCommitteeMemberForm))

    def test_add_committee_member_url(self):
        self.assertEqual(self.url,'/add_committee_member/')

    def test_view_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(reverse('add_committee_member'))
        self.assertTemplateUsed(response, 'society/committee_member_add.html')

    def test_get_add_committee_member_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_add_committee_member_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_add_committee_member_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_successful_committee_member_added(self):
        self.client.login(username=self.user.email, password='Password123')
        society = Society.objects.get(pk= self.user.pk)
        intial_member_count = society.committee_members.count()
        form = AddCommitteeMemberForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        response = self.client.post(self.url, self.form_input, follow=True)
        updated_member_count = society.committee_members.count()
        self.assertEqual(updated_member_count, intial_member_count+1 )
        self.assertTemplateUsed(response, 'society/committee_member_add.html')

    def test_unsuccessful_blank_email(self):
        self.client.login(username=self.user.email, password='Password123')
        society = Society.objects.get(pk= self.user.pk)
        intial_member_count = society.committee_members.count()
        data=self.form_input
        data['email'] = ''
        response = self.client.post(self.url, data, follow=True)
        updated_member_count = society.committee_members.count()
        self.assertEqual(intial_member_count, updated_member_count )
        self.assertTemplateUsed(response, 'society/committee_member_add.html')
    
    def test_unsuccessful_incorrect_domain_email(self):
        self.client.login(username=self.user.email, password='Password123')
        society = Society.objects.get(pk= self.user.pk)
        intial_member_count = society.committee_members.count()
        data=self.form_input
        data['email'] = 'evasmith@qmw.ac.uk'
        response = self.client.post(self.url, data, follow=True)
        updated_member_count = society.committee_members.count()
        self.assertEqual(intial_member_count, updated_member_count )
        self.assertTemplateUsed(response, 'society/committee_member_add.html')
    
    def test_button_links_present(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        list_member_url = reverse('list_committee_member')
        self.assertContains(response, list_member_url)