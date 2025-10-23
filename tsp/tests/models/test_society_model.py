"""Unit tests of the Society model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from tsp.models import Society, Student, Event

class SocietyModelTestCase(TestCase):
    """Unit tests of the Society model"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/other_events.json'
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.student = Student.objects.get(email='johndoe@kcl.ac.uk')
        # Default event and other event are organised by the society user
        self.default_event = Event.objects.get(pk=15)
        self.other_event = Event.objects.get(pk=16)

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_user_role_is_valid(self):
        self.assertEqual(self.user.role, "SOCIETY")
            
    def test_student_union_must_not_be_blank(self):
        self.user.student_union = None
        self._assert_user_is_invalid()

    # Test if the name is valid
    def test_name_must_not_be_blank(self):
        self.user.name = ''
        self._assert_user_is_invalid()

    def test_name_must_be_unique(self):
        second_user = Society.objects.get(email='ai_society@kcl.ac.uk')
        self.user.name = second_user.name
        self._assert_user_is_invalid()

    def test_name_may_contain_50_characters(self):
        self.user.name = 'x' * 50
        self._assert_user_is_valid()

    def test_name_must_not_contain_more_than_50_characters(self):
        self.user.name = 'x' * 51
        self._assert_user_is_invalid()

    # Test if the member discount is valid
    def test_member_discount_must_not_be_negative(self):
        self.user.member_discount = -1.0
        self._assert_user_is_invalid()

    def test_member_discount_may_be_zero(self):
        self.user.member_discount = 0.0
        self._assert_user_is_valid()

    def test_member_discount_may_be_positive(self):
        self.user.member_discount = 0.5
        self._assert_user_is_valid()
        
    def test_member_discount_may_be_one(self):
        self.user.member_discount = 1.0
        self._assert_user_is_valid()

    def test_member_discount_must_not_be_greater_than_one(self):
        self.user.member_discount = 1.1
        self._assert_user_is_invalid()
        
    # Test if the member fee is valid
    def test_member_fee_must_not_be_negative(self):
        self.user.member_fee = -1.0
        self._assert_user_is_invalid()
        
    def test_member_fee_may_be_zero(self):
        self.user.member_fee = 0.0
        self._assert_user_is_valid()

    def test_member_fee_may_be_positive(self):
        self.user.member_fee = 10.0
        self._assert_user_is_valid()
        
    # Test if the account number is valid
    def test_account_number_must_be_eight_digits(self):
        self.user.account_number = '123'
        self._assert_user_is_invalid()
        self.user.account_number = '123456789'
        self._assert_user_is_invalid()
        self.user.account_number = '12345678'
        self._assert_user_is_valid()

    def test_account_number_must_not_contain_letters(self):
        self.user.account_number = 'a2345678'
        self._assert_user_is_invalid()
        
    def test_account_number_must_not_contain_special_characters(self):
        self.user.account_number = '1234/$%^'
        self._assert_user_is_invalid()

    # Test if the account name is valid
    def test_account_name_may_contain_50_characters(self):
        self.user.account_name = 'a' * 50
        self._assert_user_is_valid()

    def test_account_name_must_not_contain_more_than_50_characters(self):
        self.user.account_name = 'a' * 51
        self._assert_user_is_invalid()
        
    # Test if the sort code is valid
    def test_sort_code_must_be_6_digits(self):
        self.user.sort_code = '12345'
        self._assert_user_is_invalid()
        self.user.sort_code = '1234567'
        self._assert_user_is_invalid()
        self.user.sort_code = '123456'
        self._assert_user_is_valid()

    def test_sort_code_must_not_contain_letters(self):
        self.user.sort_code = 'a23456'
        self._assert_user_is_invalid()

    def test_sort_code_must_not_contain_special_characters(self):
        self.user.sort_code = '1234/$%^'
        self._assert_user_is_invalid()
        
    # Test if the stripe account id is valid
    def test_stripe_account_id_may_contain_50_characters(self):
        self.user.stripe_account_id = 'x' * 50
        self._assert_user_is_valid()

    def test_stripe_account_id_must_not_contain_more_than_50_characters(self):
        self.user.stripe_account_id = 'x' * 51
        self._assert_user_is_invalid()
        
    def test_followers(self):
        followers = self.user.followers
        self.assertNotIn(self.student, followers)
        # Test the queryset of followers updates after the default student 
        # following the society.
        self.user.add_follower(self.student)
        followers = self.user.followers
        self.assertIn(self.student, followers)
    
    def test_subscribers(self):
        subscribers = self.user.subscribers
        self.assertNotIn(self.student, subscribers)
        # Test the queryset of subscribers updates after the default student 
        # following the society.
        self.user.add_subscriber(self.student)
        subscribers = self.user.subscribers
        self.assertIn(self.student, subscribers)
    
    def test_regular_members(self):
        regular_members = self.user.regular_members
        self.assertNotIn(self.student, regular_members)
        # Test the queryset of regular members updates after the default student 
        # becoming a regular member.
        self.user.add_regular_member(self.student)
        regular_members = self.user.regular_members
        self.assertIn(self.student, regular_members) 
    
    def test_committee_members(self):
        committee_members = self.user.committee_members
        self.assertNotIn(self.student, committee_members)
        # Test the queryset of committee members updates after the default student 
        # becoming a committee member.
        self.user.add_committee_member(self.student)
        committee_members = self.user.committee_members
        self.assertIn(self.student, committee_members)
        
    def test_upcoming_event(self):
        upcoming_events = list(self.user.upcoming_events)
        self.assertEqual(upcoming_events, [self.default_event, self.other_event])

    def test_most_upcoming_event(self):
        # Default event has an earlier start time. 
        most_upcoming_event = self.user.most_upcoming_event 
        self.assertEqual(most_upcoming_event, self.default_event)
        # Most upcoming event updates when default event is unavailable.
        self.default_event.status='CANCELLED'
        self.default_event.save()
        most_upcoming_event = self.user.most_upcoming_event 
        self.assertEqual(most_upcoming_event, self.other_event)
    
    def test_past_events(self):
        past_events = self.user.past_events
        self.assertNotIn(self.default_event, past_events)
        self.assertNotIn(self.other_event, past_events)
        # Test the queryset of past events updates after setting
        # the default event to the past.
        self.default_event.start_time = '2000-01-06T12:00:00Z'
        self.default_event.end_time = '2000-03-06T12:00:00Z'
        self.default_event.save()
        past_events = self.user.past_events 
        self.assertIn(self.default_event, past_events)
        
    def test_cancelled_events(self):
        cancelled_events = self.user.cancelled_events
        self.assertNotIn(self.default_event, cancelled_events)
        self.assertNotIn(self.other_event, cancelled_events)
        # Test the queryset of past events updates after cancelling
        # the default event.
        self.default_event.status = 'CANCELLED'
        self.default_event.save()
        cancelled_events = self.user.cancelled_events
        self.assertIn(self.default_event, cancelled_events) 
        
    def test_add_follower(self):
        self.user.add_follower(self.student)
        self.assertIn(self.student, self.user.followers)
    
    def test_add_subscriber(self):
        self.user.add_subscriber(self.student)
        self.assertIn(self.student, self.user.subscribers)
    
    def test_add_regular_member(self):
        self.user.add_regular_member(self.student)
        self.assertIn(self.student, self.user.regular_members)

    def test_add_committee_member(self):
        self.user.add_committee_member(self.student)
        self.assertIn(self.student, self.user.committee_members)
    
    def test_remove_committee_member(self):
        self.user.add_committee_member(self.student)
        self.user.remove_committee_member(self.student)
        self.assertNotIn(self.student, self.user.committee_members)

    def test_remove_follower(self):
        self.user.add_follower(self.student)
        self.user.remove_follower(self.student)
        self.assertNotIn(self.student, self.user.followers)

    def test_remove_subscriber(self):
        self.user.add_subscriber(self.student)
        self.user.remove_subscriber(self.student)
        self.assertNotIn(self.student, self.user.subscribers)
    
    def test_get_subscribers_email_list(self):
        self.user.add_subscriber(self.student)
        subscribers_emails = self.user.get_subscribers_email_list()
        self.assertListEqual([self.student.email], subscribers_emails)
    
    def test_has_bank_details_true(self):
        self.assertIsNotNone(self.user.account_name)
        self.assertIsNotNone(self.user.account_number)
        self.assertIsNotNone(self.user.sort_code)
        self.assertIsNotNone(self.user.stripe_account_id)
        self.assertTrue(self.user.has_bank_details)
        
    def test_has_bank_details_false_with_empty_account_name(self):
        self.assertTrue(self.user.has_bank_details)
        self.user.account_name = ''
        self.user.save()
        self.assertFalse(self.user.has_bank_details)
    
    def test_has_bank_details_false_with_empty_account_number(self):
        self.assertTrue(self.user.has_bank_details)
        self.user.account_number = ''
        self.user.save()
        self.assertFalse(self.user.has_bank_details)
    
    def test_has_bank_details_false_with_empty_sort_code(self):
        self.assertTrue(self.user.has_bank_details)
        self.user.sort_code = ''
        self.user.save()
        self.assertFalse(self.user.has_bank_details)
    
    def test_has_bank_details_false_with_empty_stripe_account_id(self):
        self.assertTrue(self.user.has_bank_details)
        self.user.stripe_account_id = ''
        self.user.save()
        self.assertFalse(self.user.has_bank_details)
        
    def test_accept_new_member_with_bank_details(self):
        self.user.member_fee = 10
        self.assertTrue(self.user.has_bank_details)
        self.assertTrue(self.user.accept_new_member)
    
    def test_accept_new_member_with_free_member_fee(self):
        self.user.stripe_account_id = ''
        self.user.member_fee = 0
        self.assertFalse(self.user.has_bank_details)
        # Test a society can accept new members without bank details if 
        # its member fee is free.
        self.assertTrue(self.user.accept_new_member)
    
    def test_not_accept_new_member_without_bank_details(self):
        self.user.stripe_account_id = ''
        self.user.member_fee = 10
        self.assertFalse(self.user.has_bank_details)
        self.assertFalse(self.user.accept_new_member)
        
    def test_is_student_member_when_is_committee_member(self):
        self.user.regular_member.remove(self.student)
        self.user.add_committee_member(self.student)
        is_student_member = self.user.is_student_member(self.student)
        self.assertTrue(is_student_member)
    
    def test_is_student_member_when_is_regular_member(self):
        self.user.remove_committee_member(self.student)
        self.user.add_regular_member(self.student)
        is_student_member = self.user.is_student_member(self.student)
        self.assertTrue(is_student_member)

    def test_is_not_student_member(self):
        self.user.remove_committee_member(self.student)
        self.user.regular_member.remove(self.student)
        is_student_member = self.user.is_student_member(self.student)
        self.assertFalse(is_student_member)
        
    def _assert_user_is_valid(self):
        try:    
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
