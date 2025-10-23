"""Unit tests of the committee member list view"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, Student
from tsp.forms.society.add_committee_member_form import AddCommitteeMemberForm

class ListCommitteeMembersTestCase(TestCase):
    """Unit tests of the committee member list view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.url = reverse('list_committee_member')
        self.member = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.remove = reverse('remove_committee_member')
        self.form_input = {
            'email': 'johndoe@kcl.ac.uk',
        }

    def test_get_committee_member_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_committee_member_list_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_committee_member_list_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_list_committee_member_url(self):
        self.assertEqual(self.url,'/list_committee_member/')

    def test_view_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(reverse('list_committee_member'))
        self.assertTemplateUsed(response, 'society/committee_members_list.html')

    def test_add_committee_member_form_adds_valid_student_to_list(self):
        self.client.login(username=self.user.email, password='Password123')
        society = Society.objects.get(pk= self.user.pk)
        intial_member_count = society.committee_members.count()
        form = AddCommitteeMemberForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        response = self.client.post('/add_committee_member/', self.form_input, follow=True)
        updated_member_count = society.committee_members.count()
        self.assertTemplateUsed(response, 'society/committee_member_add.html')
        self.assertEqual(updated_member_count, intial_member_count+1 )
    
    def test_add_committee_member_form_no_invalid_student_added_to_list(self):
        self.client.login(username=self.user.email, password='Password123')
        society = Society.objects.get(pk= self.user.pk)
        intial_member_count = society.committee_members.count()
        data=self.form_input
        data['email'] = 'evasmith@qmw.ac.uk'
        form = AddCommitteeMemberForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        response = self.client.post('/add_committee_member/', self.form_input, follow=True)
        updated_member_count = society.committee_members.count()
        self.assertTemplateUsed(response, 'society/committee_member_add.html')
        self.assertEqual(updated_member_count, intial_member_count )
    
    def test_successful_remove_committee_member(self):
        self.client.login(username=self.user.email, password='Password123')
        society = Society.objects.get(pk= self.user.pk)
        form = AddCommitteeMemberForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        response = self.client.post('/add_committee_member/', self.form_input, follow=True)
        intial_member_count = society.committee_members.count()
        response = self.client.post('/remove_committee_member/', data={'member_pk': self.member.pk}, follow=True)
        updated_member_count = society.committee_members.count()
        self.assertEqual(updated_member_count, intial_member_count-1 )      
        response_url = reverse('list_committee_member')
        self.assertTemplateUsed(response, 'society/committee_members_list.html')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
    
    def test_button_links_present(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        add_member_url = reverse('add_committee_member')
        self.assertContains(response, add_member_url)
        contact_member_url = reverse('contact_committee')
        self.assertContains(response, contact_member_url)