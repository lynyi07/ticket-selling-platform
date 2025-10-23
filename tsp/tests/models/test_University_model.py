"""Unit tests of the University model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from tsp.models import University, Domain

class UniversityModelTestCase(TestCase):
    """Unit tests of the University model"""

    fixtures = [
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self):
        self.domain = Domain.objects.get(name='kcl.ac.uk')
        self.university = University.objects.get(name="King's College London")

    def test_valid_university(self):
        try:
            university = University.objects.get(name="King's College London")
        except University.DoesNotExist:
            self.fail('University instance not found')
        self.assertIsNotNone(university)

    def test_name_must_not_be_blank(self):
        self.university.name = ''
        with self.assertRaises(ValidationError):
            self.university.full_clean()

    def test_abbreviation_must_not_be_blank(self):
        self.university.abbreviation = ''
        with self.assertRaises(ValidationError):
            self.university.full_clean()
            
    def test_university_has_related_domains(self):
        domains = self.university.domains.all()
        self.assertIn(self.domain, domains)
        self.assertEqual(domains.count(), 1)

    def test_domains_property_returns_all_domains_related_to_university(self):
        second_domain = Domain.objects.create(
            name='kcl.edu', 
            university=self.university
        )
        domains = self.university.domains.all()
        self.assertIn(self.domain, domains)
        self.assertIn(second_domain, domains)
        self.assertEqual(domains.count(), 2)