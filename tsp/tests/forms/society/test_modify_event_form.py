"""Unit tests of the modify event form"""
import os
from ticket_selling_platform import settings
from django.test import TestCase
from django.utils import timezone
from tsp.models import Society, Event
from tsp.forms.society.modify_event_form import ModifyEventForm

class ModifyEventFormTestCase(TestCase):
    """Unit tests of the modify event form"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_event.json'
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.default_photo = os.path.join(
            settings.MEDIA_ROOT,
            'default_event_photo.jpg'
        )
        self.event = Event.objects.get(pk=15)
        self.form_input = {
            'name': 'Test Event Name',
            'description': 'This is a test event.',
            'location': 'Test location',
            'photo': self.default_photo,
            'start_time': timezone.now() + timezone.timedelta(days=1),
            'end_time': timezone.now() + timezone.timedelta(days=1, hours=2),
            'early_booking_capacity': self.event.early_booking_capacity,
            'standard_booking_capacity': self.event.standard_booking_capacity,
            'standard_price': self.event.standard_price,
            'early_bird_price': self.event.early_bird_price,
            'event_id': 16
        }
    
    def test_valid_form(self):
        form = ModifyEventForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_neccessary_fields(self):
        form = ModifyEventForm(data=self.form_input)
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('start_time', form.fields)
        self.assertIn('end_time', form.fields)
        self.assertIn('early_booking_capacity', form.fields)
        self.assertIn('standard_booking_capacity', form.fields)
        self.assertIn('standard_price', form.fields)
        self.assertIn('early_bird_price', form.fields)
        self.assertIn('photo', form.fields)
    
    def test_modify_with_invalid_standard_booking_capacity(self):
        standard_booking_capacity = self.event.standard_booking_capacity - 1
        self.form_input['standard_booking_capacity'] = standard_booking_capacity
        form = ModifyEventForm(data=self.form_input, event=self.event)
        self.assertFalse(form.is_valid())
        self.assertIn('standard_booking_capacity', form.errors)
        self.assertEqual(
            form.errors['standard_booking_capacity'][0], 
            "You can not decrease regular booking capacity."    
        )