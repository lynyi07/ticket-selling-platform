"""Unit tests of the Student model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tsp.models import Student, Event

class StudentModelTestCase(TestCase):
    """Unit tests of the Student model"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json'
    ]

    def setUp(self):
        self.user = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.event = Event.objects.get(name='Default test event')

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_user_role_is_valid(self):
        self.assertEqual(self.user.role, "STUDENT")

    # Test if the first name is valid
    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        second_user = Student.objects.get(email='janedoe@kcl.ac.uk')
        self.user.first_name = second_user.first_name
        self._assert_user_is_valid()

    def test_first_name_may_contain_50_characters(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()

    # Test if the last name is valid
    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        second_user = Student.objects.get(email='janedoe@kcl.ac.uk')
        self.user.last_name = second_user.last_name
        self._assert_user_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()
        
    # Test saved_event field
    def test_saved_event_is_blank_by_default(self):
        current_saved_events = self.user.saved_event.all()
        self.assertFalse(current_saved_events.exists())

    def test_saved_event_can_be_added(self):
        self.user.saved_event.add(self.event)
        current_saved_events = self.user.saved_event.all()
        self.assertTrue(current_saved_events.exists())
        self.assertIn(self.event, current_saved_events) 
    
    def test_saved_event_can_be_removed(self):
        self.user.saved_event.add(self.event)
        self.user.saved_event.remove(self.event)
        current_saved_events = self.user.saved_event.all()
        self.assertFalse(current_saved_events.exists())
        
    # Test discounted_event field
    def test_discounted_event_is_blank_by_default(self):
        current_discounted_events = self.user.discounted_event.all()
        self.assertFalse(current_discounted_events.exists())
        
    def test_discounted_event_can_be_added(self):
        self.user.discounted_event.add(self.event)
        current_discounted_events = self.user.discounted_event.all()
        self.assertTrue(current_discounted_events.exists())
        self.assertIn(self.event, current_discounted_events)
        
    # Test purchased_event field
    def test_purchased_event_is_blank_by_default(self):
        current_purchased_events = self.user.purchased_event.all()
        self.assertFalse(current_purchased_events.exists())
        
    def test_purchased_event_can_be_added(self):
        self.user.purchased_event.add(self.event)
        current_purchased_events = self.user.purchased_event.all()
        self.assertTrue(current_purchased_events.exists())
        self.assertIn(self.event, current_purchased_events)
        
    def test_full_name(self):
        expected_full_name = 'John Doe'
        self.assertEqual(self.user.full_name, expected_full_name)
        
        # Test that changing the first name updates the full name.
        self.user.first_name = 'Jane'
        self.user.save()
        expected_full_name = 'Jane Doe'
        self.assertEqual(self.user.full_name, expected_full_name)
        
        # Test that changing the last name updates the full name.
        self.user.last_name = 'Smith'
        self.user.save()
        expected_full_name = 'Jane Smith'
        self.assertEqual(self.user.full_name, expected_full_name)
    
    def test_save_event(self):
        self.user.save_event(self.event)
        saved_events = self.user.saved_event.all()
        self.assertIn(self.event, saved_events)
        
    def test_unsave_event(self):
        self.user.save_event(self.event)
        count_before = self.user.saved_event.count()
        self.user.unsave_event(self.event)
        count_after = self.user.saved_event.count()
        self.assertEqual(count_before - 1, count_after)
        saved_events = self.user.saved_event.all()
        self.assertNotIn(self.event, saved_events)
        
    def test_event_saved(self):
        event_saved = self.user.event_saved(self.event)
        self.assertFalse(event_saved)        
        # Test that the return value updates after the event is saved. 
        self.user.save_event(self.event)
        event_saved = self.user.event_saved(self.event)
        self.assertTrue(event_saved)
        
    def test_purchase_event(self):
        self.user.purchase_event(self.event)
        purchased_events = self.user.purchased_event.all()
        self.assertIn(self.event, purchased_events)
        
    def test_purchase_discounted_event(self):
        self.user.purchase_discounted_event(self.event)
        discounted_events = self.user.discounted_event.all()
        self.assertIn(self.event, discounted_events)

    def test_event_discounted(self):
        event_discounted = self.user.event_discounted(self.event)
        self.assertFalse(event_discounted)
        # Test that the return value updates after the event is purchased with 
        # discount applied.
        self.user.purchase_discounted_event(self.event)
        event_discounted = self.user.event_discounted(self.event)
        self.assertTrue(event_discounted)
        
    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()