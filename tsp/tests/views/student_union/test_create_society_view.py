"""Unit tests of the create society view"""
from django.test import TestCase
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from tsp.tests.helpers import reverse_with_next
from tsp.models import Society, StudentUnion
from tsp.forms.student_union.create_society_form import CreateSocietyForm

class CreateSocietyViewTestCase(TestCase):
    """Unit tests of the create society view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json'  
    ]

    def setUp(self):
        self.user = StudentUnion.objects.get(email='kclsu@kcl.ac.uk')
        self.url = reverse('create_society')
        self.form_input = {
            "name": "AI",
            "email": "aisoc@kcl.ac.uk",
        }
    
    def test_request_url(self):
        self.assertEqual(self.url, '/create_society/')
    
    def test_get_create_society(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_union/create_society.html')   # Check whether correct template has been used
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateSocietyForm))
        self.assertFalse(form.is_bound)
    
    def test_successful_create_society(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = Society.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Society.objects.count()
        self.assertEqual(after_count, before_count + 1)             #checks if number of students has increased by one
        society = Society.objects.get(email = "aisoc@kcl.ac.uk")       # Validating student's details
        self.assertEqual(society.name, 'KCL AI')
        self.assertEqual(society.email, "aisoc@kcl.ac.uk")
        check_password('Password123', society.password)
        redirect_url = reverse('view_societies')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
    
    def test_successful_create_society_with_different_university_and_same_name(self):
        self.client.login(email='qmusu@qmw.ac.uk', password='Password123')
        self.form_input['email'] = 'tech_society@qmw.ac.uk'
        self.form_input['name'] = 'Tech society'
        before_count = Society.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Society.objects.count()
        self.assertEqual(after_count, before_count + 1)             #checks if number of students has increased by one
        society = Society.objects.get(email = "tech_society@qmw.ac.uk")       # Validating student's details
        self.assertEqual(society.name, 'QMU Tech society')
        self.assertEqual(society.email, "tech_society@qmw.ac.uk")
        check_password('Password123', society.password)
        redirect_url = reverse('view_societies')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
    
    def test_unsuccessful_create_society(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['email'] = 'notemail'
        before_count = Society.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Society.objects.count()
        self.assertEqual(after_count, before_count)             #checks if number of societies is the same
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_union/create_society.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateSocietyForm))
        self.assertTrue(form.is_bound)
        self.assertFormError(response, 'form', field='email', errors='Enter a valid email address.')

    def test_unsuccessful_create_society_with_already_existing_name(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['email'] = 'tech@kcl.ac.uk'
        self.form_input['name'] = 'Tech society'
        before_count = Society.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Society.objects.count()
        self.assertEqual(after_count, before_count)             #checks if number of societies is the same
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_union/create_society.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateSocietyForm))
        self.assertTrue(form.is_bound)
        self.assertFormError(response, 'form', field='name', errors='A society with this name already exists')

    def test_unsuccessful_create_society_with_different_university_domain(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['email'] = 'aisoc@qmw.ac.uk'
        before_count = Society.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Society.objects.count()
        self.assertEqual(after_count, before_count)             #checks if number of societies is the same
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_union/create_society.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateSocietyForm))
        self.assertTrue(form.is_bound)
        self.assertFormError(response, 'form', field='email', errors='Domain is not valid')

    def test_get_create_society_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_create_society_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_create_society_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')