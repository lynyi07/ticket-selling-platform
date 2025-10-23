"""Unit tests of the Domain model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from tsp.models import University, Domain

class DomainModelTestCase(TestCase):
    """Unit tests of the Domain model"""

    fixtures = [
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self):
        self.domain = Domain.objects.get(name='kcl.ac.uk')
        self.university = University.objects.get(name="King's College London")
    
    def test_valid_domain(self):
        self.assertIsNotNone(self.domain)

    def test_domain_name_must_not_be_blank(self):
        self.domain.name = ''
        with self.assertRaises(ValidationError):
            self.domain.full_clean()
        
    def test_domain_belongs_to_university(self):
        self.assertEqual(self.domain.university, self.university)