"""Unit tests of the all societies page view"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, Event, Student

class AllSocietiesViewTestCase(TestCase):
    """Unit tests of the all societies page view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json'
    ]

    def setUp(self):
        self.user = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.url = reverse('all_societies')
        self.event = Event.objects.get(pk=15)
        self.societies = list(Society.objects.filter(university=self.user.university))
        self.societies[0], self.societies[1] = self.societies[1], self.societies[0]

    def test_url(self):
        self.assertEqual(self.url, '/all_societies/')

    def test_get_all_societies_page_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(reverse('all_societies'))
        self.assertTemplateUsed(response, 'student/all_societies.html')

    def test_get_all_societies_page_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_all_societies_page_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_all_societies_page_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_all_societies_page_displays_all_societies_by_default(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['search'], '')
        self.assertEqual(len(response.context['object_list']), len(self.societies))
        self.assertQuerysetEqual(response.context['object_list'], self.societies)

    def test_get_all_societies_page_displays_all_societies(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester('All', '', self.societies)

    def test_get_all_societies_page_displays_all_societies_with_search(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester('All', 'Tech', [self.societies[1]])

    def test_get_all_societies_page_displays_all_societies_of_a_specific_university(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester("King's College London", '', self.societies[:2])

    def test_get_all_societies_page_displays_all_societies_of_a_specific_university_with_search(self):
        self.client.login(email=self.user.email, password='Password123')
        self._tester("King's College London", 'AI', [self.societies[0]])

    def _tester(self, selected_option_in, search_in, object_list_in):
        """
        Tests whether the correct societies are presented given that 
        filters may be applied.

        Parameters
        ----------
        selected_option_in : string
            The inputted option to filter for societies from a specific university.
        search_in : string
            The inputted search query.
        object_list_in : list
            The list of societies that are supposed to be included in the GET request.
        """

        response = self.client.get(self.url, {'ordering': selected_option_in, 'search': search_in})
        self.assertEqual(response.context['search'], search_in)
        self.assertEqual(len(response.context['object_list']), len(object_list_in))
        self.assertQuerysetEqual(response.context['object_list'], object_list_in)
    
    def test_button_links_present(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        view_society_url = reverse('society_page', kwargs={'pk':self.societies[0].pk})
        self.assertContains(response, view_society_url)
        