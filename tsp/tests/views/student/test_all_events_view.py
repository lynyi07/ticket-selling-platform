"""Unit tests of the all events page view"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, Event, Student
from datetime import datetime, timedelta
from django.utils import timezone

class AllEventsViewTestCase(TestCase):
    """Unit tests of the all events page view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/other_events.json'
    ]

    def setUp(self):
        self.user = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.url = reverse('all_events')
        self.event1 = Event.objects.get(pk=15)
        self.event2 = Event.objects.get(pk=16)
        self.society = Society.objects.get(name="KCL Tech society")
        self.cancelled_events = self._create_cancelled_events(self.society)
        self.past_events = self._create_past_events(self.society)
        self.upcoming_events = [self.event1, self.event2]

    def test_url(self):
        self.assertEqual(self.url, '/all_events/')

    def test_view_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(reverse('all_events'))
        self.assertTemplateUsed(response, 'student/all_events.html')

    def test_get_all_events_uses_correct_context_data(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(reverse('all_events'))
        self.assertEqual(response.context['selected_date_option'], 'EARLIEST')
        self.assertEqual(response.context['selected_status_option'], 'UPCOMING')
        self.assertEqual(response.context['search'], '')
        self.assertEqual(response.context['date_options'], [("EARLIEST", "Earliest"), ("LATEST", "Latest")])
        self.assertEqual(response.context['status_options'], [("UPCOMING", "Upcoming"), ("PAST", "Past"), ("CANCELLED", "Cancelled")])

    def test_get_all_events_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_all_events_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_all_events_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_all_events_displays_earliest_by_default(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['selected_date_option'], 'EARLIEST')
        self.assertEqual(response.context['selected_status_option'], 'UPCOMING')
        self.assertEqual(response.context['search'], '')
        for event in self.upcoming_events:
            self.assertContains(response, event.name)
            self.assertContains(response, event.location)
            self.assertContains(response, event.photo.url)
        self.assertEqual(len(response.context['object_list']), 2)
        self.assertQuerysetEqual(response.context['object_list'], self.upcoming_events)
        
    def test_get_all_events_displays_earliest_upcoming_events_when_selected(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester('EARLIEST', 'UPCOMING', '', self.upcoming_events)

    def test_get_all_events_displays_latest_upcoming_events_when_selected(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester('LATEST', 'UPCOMING', '', list(reversed(self.upcoming_events)))

    def test_get_all_events_displays_earliest_upcoming_events_that_are_searched(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester('EARLIEST', 'UPCOMING', 'default', [self.event1])

    def test_get_all_events_displays_earliest_past_events_when_selected(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester('EARLIEST', 'PAST', '', list(reversed(self.past_events)))

    def test_get_all_events_displays_latest_past_events_when_selected(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester('LATEST', 'PAST', '', self.past_events)

    def test_get_all_events_displays_earliest_past_events_that_are_searched(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester('EARLIEST', 'PAST', '0', [self.past_events[0]])

    def test_get_all_events_displays_earliest_cancelled_events_when_selected(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester('EARLIEST', 'CANCELLED', '', self.cancelled_events[1:])

    def test_get_all_events_displays_latest_cancelled_events_when_selected(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester('LATEST', 'CANCELLED', '', list(reversed(self.cancelled_events[1:])))

    def test_get_all_events_displays_earliest_cancelled_events_that_are_searched(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester('EARLIEST', 'CANCELLED', '1', [self.cancelled_events[1]])

    def _tester(self, date_filter_in, status_filter_in, search_in, object_list_in):
        """
        Tests whether the correct events are presented given that 
        filters may be applied.

        Parameters
        ----------
        date_filter_in: 
            The inputted date status to filter for events.
        status_filter_in : string
            The inputted status to filter for events.
        search_in : string
            The inputted search query.
        object_list_in : list
            The list of events that are supposed to be included in the GET request.
        """

        response = self.client.get(self.url, {'date_filter' : date_filter_in, 'status_filter' : status_filter_in, 'search' : search_in})
        self.assertEqual(response.context['selected_date_option'], date_filter_in)
        self.assertEqual(response.context['selected_status_option'], status_filter_in)
        self.assertEqual(response.context['search'], search_in)
        for event in object_list_in:
            self.assertContains(response, event.name)
            self.assertContains(response, event.location)
            self.assertContains(response, event.photo.url)
        self.assertEqual(len(response.context['object_list']), len(object_list_in))
        self.assertQuerysetEqual(response.context['object_list'], object_list_in)

    def _create_cancelled_events(self, society_in):
        """
        Create cancelled events.
        
        Parameters
        ----------
        society_in : Society
            The Society object.

        Returns
        -------
        list
            The list of cancelled events created.
        """

        cancelled_events = []
        for i in range(3):
            if i == 1:
                start_date = (datetime.now() + timedelta(days=10)).replace(tzinfo=timezone.get_current_timezone())
            elif i == 2:
                start_date = (datetime.now() + timedelta(days=20)).replace(tzinfo=timezone.get_current_timezone())
            else:
                start_date = (datetime.now() - timedelta(days=10)).replace(tzinfo=timezone.get_current_timezone())
            event = Event.objects.create(
                host = society_in,
                name = f'Cancelled event.{i}',
                description = f'Test event {i}',
                location = f'Test address {i}',
                start_time = start_date,
                end_time = (start_date + timedelta(hours=10)).replace(tzinfo=timezone.get_current_timezone()),
                early_booking_capacity = 10,
                standard_booking_capacity = 20,
                early_bird_price = 5,
                standard_price = 5,
                status = 'CANCELLED',
                photo = '/static/images/default_event_photo.jpg'
            )
            event.society.add(society_in)
            cancelled_events.append(event)
        return cancelled_events
    
    def _create_past_events(self, society_in):
        """
        Create past events.

        Parameters
        ----------
        society_in : Society
            The Society object.

        Returns
        -------
        list
            The list of past events created.
        """

        past_events = []
        for i in range(2):
            if i == 1:
                start_date = (datetime.now() - timedelta(days=100)).replace(tzinfo=timezone.get_current_timezone())
            else:
                start_date = (datetime.now() - timedelta(days=50)).replace(tzinfo=timezone.get_current_timezone())
            event = Event.objects.create(
                host = society_in,
                name = f'Past event.{i}',
                description = f'Test event {i}',
                location = f'Test address {i}',
                start_time = start_date,
                end_time = (start_date + timedelta(hours=10)).replace(tzinfo=timezone.get_current_timezone()),
                early_booking_capacity = 10,
                standard_booking_capacity = 20,
                early_bird_price = 5,
                standard_price = 5,
                status = 'ACTIVE',
                photo = '/static/images/default_event_photo.jpg'
            )
            event.society.add(society_in)
            past_events.append(event)
        return past_events

    def test_button_links_present(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        event_page_url = reverse('event_page', kwargs={'pk':self.event1.pk})
        self.assertContains(response, event_page_url)
        