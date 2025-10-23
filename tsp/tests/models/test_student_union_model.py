"""Unit tests of the Student Union model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from tsp.models import StudentUnion

class StudentUnionModelTestCase(TestCase):
    """Unit tests of the Student Union model"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json'
    ]

    def setUp(self):
        self.user = StudentUnion.objects.get(email='kclsu@kcl.ac.uk')

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_user_role_is_valid(self):
        self.assertEqual(self.user.role, "STUDENT_UNION")

    # Test if the name is valid
    def test_name_must_not_be_blank(self):
        self.user.name = ''
        self._assert_user_is_invalid()

    def test_name_must_not_be_unique(self):
        second_user = StudentUnion.objects.get(email='uclsu@ucl.ac.uk')
        self.user.name = second_user.name
        self._assert_user_is_valid()

    def test_name_may_contain_50_characters(self):
        self.user.name = 'x' * 50
        self._assert_user_is_valid()

    def test_name_must_not_contain_more_than_50_characters(self):
        self.user.name = 'x' * 51
        self._assert_user_is_invalid()
        
    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()