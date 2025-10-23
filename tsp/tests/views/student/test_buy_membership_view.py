"""Unit tests of the buy membership view"""
from django.test import TestCase 
from django.urls import reverse
from tsp.tests.helpers import reverse_with_next
from tsp.models import Student, Cart, Society

class BuyMembershipViewTestCase(TestCase):
    """Unit tests of the buy membership view"""
    
    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/default_cart.json'
    ]
    
    def setUp(self):
        self.user = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.cart = Cart.objects.get(student=self.user)
        self.society = Society.objects.get(email='ai_society@kcl.ac.uk')   
        self.other_society = Society.objects.get(email='tech_society@kcl.ac.uk')      
        self.url = reverse('buy_membership')     
    
    def test_request_url(self):
        self.assertEqual(self.url, '/buy_membership/')
    
    def test_successful_buy_membership(self):
        # Test the membership is added to cart successfully.
        memberships = self.cart.membership.all()
        self.assertNotIn(self.society, memberships)
        self.client.login(email=self.user.email, password='Password123')
        before_count = self.cart.membership.count()
        response = self.client.post(self.url, {'society_pk': self.society.pk}, follow=True)
        response_url = reverse('cart_detail')
        self.assertRedirects(response, response_url, 302, 200)
        self.cart.refresh_from_db()
        after_count = self.cart.membership.count()
        memberships = self.cart.membership.all()
        self.assertIn(self.society, memberships)
        self.assertEqual(before_count+1, after_count)

    def test_buy_membership_when_already_in_cart(self):
        # Test user can not add duplicated membership to cart.
        memberships = self.cart.membership.all()
        self.assertIn(self.other_society, memberships)
        self.client.login(email=self.user.email, password='Password123')
        before_count = self.cart.membership.count()
        response = self.client.post(self.url, {'society_pk': self.other_society.pk}, follow=True)
        response_url = reverse('cart_detail')
        self.assertRedirects(response, response_url, 302, 200)
        self.cart.refresh_from_db()
        after_count = self.cart.membership.count()
        self.assertEqual(before_count, after_count)
        
    def test_get_buy_membership_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_buy_membership_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
     