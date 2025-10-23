"""Unit tests of the contact committee members view"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.forms.society.contact_members_form import ContactCommitteeMembersForm
from tsp.models import Society, Student
from django.core import mail

class ContactCommitteeMembersTestCase(TestCase): 
    """Unit tests of the contact committee members view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self):
        self.form_input = {
            'email_header': 'Test Email',
            'email_message': 'This is a test email.'
        } 
        self.url = reverse('contact_committee') 
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk') 

    def test_contact_committee_url(self): 
        self.assertEqual(self.url,'/contact_committee_members/')
    
    def test_get_contact_committee_members(self):
        self.client.login(email=self.society.email, password='Password123')
        response = self.client.get(self.url)
        form = response.context['form']
        self.assertTrue(isinstance(form, ContactCommitteeMembersForm))

    def test_contact_member_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_contact_member_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_contact_member_list_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_view_uses_correct_template(self):
        self.client.login(email=self.society.email, password='Password123')
        response = self.client.get(reverse('contact_committee'))
        self.assertTemplateUsed(response, 'society/contact_committee_members.html')
    
    def test_button_links_present(self):
        self.client.login(username=self.society.email, password='Password123')
        response = self.client.get(self.url)
        list_member_url = reverse('list_committee_member')
        self.assertContains(response, list_member_url)

    def test_post_contact_committee_members_with_valid_data(self):
        self.client.login(username=self.society.email, password='Password123')
        student = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.society.committee_member.add(student)
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertTemplateUsed(response, 'society/contact_committee_members.html')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Email')
        self.assertEqual(mail.outbox[0].body, 'This is a test email.')
        self.assertEqual(mail.outbox[0].to, ['johndoe@kcl.ac.uk'])
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_post_contact_committee_members_with_invalid_data(self):
        self.client.login(username=self.society.email, password='Password123')
        student = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.society.committee_member.add(student)
        self.form_input['email_header'] = ''
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertTemplateUsed(response, 'society/contact_committee_members.html')
        self.assertEqual(len(mail.outbox), 0)