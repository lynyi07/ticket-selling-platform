"""Unit tests of the add committee member form"""
from django.test import TestCase
from tsp.models import Society, Student
from tsp.forms.society.add_committee_member_form import AddCommitteeMemberForm

class AddCommitteeMemberFormTestCase(TestCase):
    """Unit tests of the add committee member form"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json', 
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json'  
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.student = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.form_input = {
            'email' : self.student.email,
        }

    def test_form_has_necessary_fields(self):
        form = AddCommitteeMemberForm()
        self.assertIn('email', form.fields)
         
    def test_valid_form(self):
        form = AddCommitteeMemberForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        
    def test_form_invalid_with_non_student_email(self):
        self.form_input['email'] = 'johndoe@gmail.com'
        form = AddCommitteeMemberForm(data=self.form_input, society=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'This email does not belong to any student.', 
            form.errors['email']
        )
        
    def test_form_invalid_with_invalid_email(self):
        self.form_input['email'] = 'johndoe'
        form = AddCommitteeMemberForm(data=self.form_input, society=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'This email does not belong to any student.', 
            form.errors['email']
        )
        
    def test_form_invalid_with_existing_committee_member_email(self):
        self.user.add_committee_member(self.student)
        form = AddCommitteeMemberForm(data=self.form_input, society=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'The student is already a committee member of this society.', 
            form.errors['email']
        )
        
    def test_form_invalid_with_email_from_other_university(self):
        self.form_input['email'] = 'evasmith@qmw.ac.uk'
        form = AddCommitteeMemberForm(data=self.form_input, society=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'This student does not belong to the same university as the society.', 
            form.errors['email']
        )
        
        