"""Unit tests of the for you page view"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, Event, Student

class ForYouPageViewTestCase(TestCase):
    """Unit tests of the for you page view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_event.json'
    ]

    def setUp(self):
        self.user = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.url = reverse('for_you_page')
        self.event = Event.objects.get(pk=15)
        self.society = Society.objects.get(name="KCL Tech society")

    def test_url(self):
        self.assertEqual(self.url, '/for_you_page/')

    def test_view_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(reverse('for_you_page'))
        self.assertTemplateUsed(response, 'student/for_you_page.html')

    def test_get_for_you_page_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_for_you_page_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_for_you_page_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_view_displays_all_events_by_default(self):
        self.client.login(email=self.user.email, password='Password123')
        self.society.add_follower(self.user)
        self.society.save()
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['object_list'], [self.event])

    def test_view_displays_all_events(self):
        self.client.login(email=self.user.email, password='Password123')
        self.society.add_follower(self.user)
        self.society.save()
        response = self.client.get(self.url, {'followed_list': 'All'})
        self.assertQuerysetEqual(response.context['object_list'], [self.event])

    def test_view_displays_a_specific_university_events(self):
        self.client.login(email=self.user.email, password='Password123')
        self.society.add_follower(self.user)
        self.society.save()
        response = self.client.get(self.url, {'followed_list': "King's College London"})
        self.assertQuerysetEqual(response.context['object_list'], [self.event])

    def test_button_links_present(self):
        self.client.login(username=self.user.email, password='Password123')
        self.society.add_follower(self.user)
        self.society.save()
        response = self.client.get(self.url, {'followed_list': "King's College London"})
        event_page_url = reverse('event_page', kwargs={'pk':self.event.pk})
        self.assertContains(response, event_page_url)
        