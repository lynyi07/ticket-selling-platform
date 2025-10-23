"""Unit tests of the regular member list view"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society,Student

class ListRegularMembersTestCase(TestCase):
    """Unit tests of the regular member list view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.url = reverse('list_regular_member')
        self.member = Student.objects.get(email='johndoe@kcl.ac.uk')
       
    def test_get_list_regular_member_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_regular_member_list_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_regular_member_list_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_list_regular_member_url(self):
        self.assertEqual(self.url,'/list_regular_member/')

    def test_view_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(reverse('list_regular_member'))
        self.assertTemplateUsed(response, 'society/regular_members_list.html')
    
    def test_add_regular_members(self):
        self.client.login(email=self.user.email, password='Password123')
        society = Society.objects.get(pk= self.user.pk)
        intial_member_count = society.regular_members.count()
        society.add_regular_member(self.member)
        updated_member_count = society.regular_members.count()
        self.assertEqual(updated_member_count, intial_member_count+1 )
    
    def test_template_content_headings(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)     
        self.assertContains(response, "Society Members")
    
    def test_button_links_present(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        member_discount_url = reverse('member_discount')
        self.assertContains(response,member_discount_url)
        member_fee_url = reverse('member_fee')
        self.assertContains(response, member_fee_url)
