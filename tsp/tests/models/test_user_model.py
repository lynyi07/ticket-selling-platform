"""Unit tests of the User model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TransactionTestCase
from tsp.models import User, University, Student, Society, StudentUnion

class UserModelTestCase(TransactionTestCase):
    """Unit tests of the User model"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json'  
    ]
    
    def setUp(self):
        self.student = User.objects.get(pk=1)
        self.society = User.objects.get(pk=5)
        self.student_union = User.objects.get(pk=3)
        self.user_data = [
            (self.student.email.lower(), User.Role.STUDENT),
            (self.society.email.lower(), User.Role.SOCIETY),
            (self.student_union.email.lower(), User.Role.STUDENT_UNION),
        ]
        
    def test_valid_user(self):
        self._assert_user_is_valid(self.student)
        self._assert_user_is_valid(self.student_union)
        self._assert_user_is_valid(self.society)

    def test_user_role_is_valid(self):
        self.assertEqual(self.student.role, User.Role.STUDENT)
        self.assertEqual(self.student_union.role, User.Role.STUDENT_UNION)
        self.assertEqual(self.society.role, User.Role.SOCIETY)

    def test_email_must_be_unique(self):
        for email, role in self.user_data:
            try:
                invalid_user = User.objects.create(email=email, role=role)
            except IntegrityError:
                pass
            
    def test_role_must_be_valid(self):
        invalid_user = User.objects.create(
            email='email@kcl.ac.uk',
            role='INVALID_ROLE'
        )
        self._assert_user_is_invalid(invalid_user)
    
    def test_default_role_is_student(self):
        # Create a user with no role specified
        user = User.objects.create(email='default_role_user@kcl.ac.uk')
        self.assertEqual(user.role, User.Role.STUDENT)

    def _assert_user_is_valid(self, user):
        try:
            user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')
    
    def _assert_user_is_invalid(self, user):
        with self.assertRaises(ValidationError):
            user.full_clean()
