"""Unit tests of the Event model"""
import os
from ticket_selling_platform import settings
from django.test import TestCase
from tsp.models import Event, Society, University, Student
from datetime import datetime
import pytz

class EventModelTestCase(TestCase):
    """Unit tests of the Event model"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json'
    ]

    def setUp(self):
        self.event = Event.objects.get(name='Default test event')
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.university = University.objects.get(name="King's College London")
        self.student = Student.objects.get(email='johndoe@kcl.ac.uk')

    def test_valid_event(self):
        try:
            self.event = Event.objects.get(pk=15)
        except Event.DoesNotExist:
            self.fail('Event instance not found')
        self.assertIsNotNone(self.event)

    def test_default_status(self):
        self.assertEqual(self.event.status, "ACTIVE")
        
    def test_event_host(self):
        self.assertEqual(self.event.host, self.society)
    
    def test_event_society(self):
        self.assertIn(self.society, self.event.society.all())
    
    def test_event_name(self):
        self.assertEqual(self.event.name, 'Default test event')
        
    def test_event_description(self):
        self.assertEqual(self.event.description, 'This is a default test event')
        
    def test_event_location(self):
        self.assertEqual(self.event.location, 'Default test location')
        
    def test_event_start_time(self):
        self.assertEqual(
            self.event.start_time, 
            datetime(2030, 2, 6, 12, 0, 0, tzinfo=pytz.UTC)
        )

    def test_event_end_time(self):
        self.assertEqual(
            self.event.end_time, 
            datetime(2030, 2, 7, 12, 0, 0, tzinfo=pytz.UTC)
        )

    def test_event_early_booking_capacity(self):
        self.assertEqual(self.event.early_booking_capacity, 50)

    def test_event_standard_booking_capacity(self):
        self.assertEqual(self.event.standard_booking_capacity, 100)

    def test_event_early_bird_price(self):
        self.assertEqual(self.event.early_bird_price, 3.0)

    def test_event_standard_price(self):
        self.assertEqual(self.event.standard_price, 5.0)

    def test_default_photo(self):
        default_photo = os.path.join(
            settings.MEDIA_ROOT,
            'default_event_photo.jpg'
        )
        self.assertEqual(
            self.event.photo.path,
            default_photo
        )
        
    def test_cancel_event(self):
        self.event.cancel_event()
        self.assertEqual(self.event.status, Event.Status.CANCELLED)
    
    def test_event_is_active(self):
        self.assertTrue(self.event.is_active)
        self.event.cancel_event()
        self.assertFalse(self.event.is_active)

    def test_get_event_ticket_inventory_for_early_bird_ticket(self):
        inventory = Event.get_event_ticket_inventory(self.event, 'early_bird')
        self.assertEqual(inventory, 50)
    
    def test_get_event_ticket_inventory_for_standard_ticket(self):
        inventory = Event.get_event_ticket_inventory(self.event, 'standard')
        self.assertEqual(inventory, 100)

    def test_get_event_ticket_inventory_for_invalid_ticket_type(self):
        # Test that the method raises a ValueError when an invalid ticket type 
        # is specified.
        with self.assertRaises(ValueError):
            Event.get_event_ticket_inventory(self.event, 'invalid_ticket_type')

    def test_event_savers(self):
        # Test that the student does not save the event at first.
        students = self.event.event_savers
        self.assertNotIn(self.student, students)
        count_before = students.count()
        # Test that the event's list of saved students updates correctly 
        # after a student saves this event.
        self.student.save_event(self.event)
        students = self.event.event_savers
        count_after = students.count()
        self.assertIn(self.student, students)
        self.assertEqual(count_after, count_before+1)

    def test_event_buyers(self):
        # Test that the student does not purchase the event ticket at first.
        students = self.event.event_buyers
        self.assertNotIn(self.student, students)
        count_before = students.count()
        # Test that the event's list of buyers updates correctly after 
        # a student purchases this event ticket.
        self.student.purchase_event(self.event)
        students = self.event.event_buyers
        count_after = students.count()
        self.assertIn(self.student, students)
        self.assertEqual(count_after, count_before+1)
