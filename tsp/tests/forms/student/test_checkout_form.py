"""Unit tests of the checkout form"""
from django.test import TestCase
from tsp.models import Student, Cart
from tsp.forms.student.checkout_form import CheckoutForm
from django.test import RequestFactory

class CheckOutFormTestCase(TestCase):
    """Unit tests of the checkout form"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/default_cart.json'
    ]

    def setUp(self):
        self.student = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.cart = Cart.objects.get(student=self.student)
        self.form_input = {
            'payment_method_id': 'payment_method_id_test',
            'full_name': self.student.full_name,
            'email': self.student.email,
            'line_1': 'Strand',
            'line_2': "King's College London",
            'city_town': 'London',
            'postcode': 'WC2R 2LS',
            'country': 'United Kingdom',
            'amount': self.cart.total_price
        }   
        self.factory = RequestFactory()
        
    def test_valid_form(self):
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_form_has_necessary_fields(self):
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertIn('payment_method_id', form.fields)
        self.assertIn('full_name', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('line_1', form.fields)
        self.assertIn('line_2', form.fields)
        self.assertIn('city_town', form.fields)
        self.assertIn('postcode', form.fields)
        self.assertIn('country', form.fields)
        self.assertIn('amount', form.fields)
    
    def test_payment_method_id_must_not_be_empty(self):
        self.form_input['payment_method_id'] = ''
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['payment_method_id'][0], 'This field is required.')
        
    def test_full_name_must_not_be_empty(self):
        self.form_input['full_name'] = ''
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['full_name'][0], 'This field is required.')
    
    def test_full_name_max_length(self):
        self.form_input['full_name'] = 'x' * 255
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertTrue(form.is_valid())
        self.form_input['full_name'] = 'x' * 256
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(
            form.errors['full_name'][0], 
            'Ensure this value has at most 255 characters (it has 256).'
        )
    
    def test_email_must_not_be_empty(self):
        self.form_input['email'] = ''
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['email'][0], 'This field is required.')
        
    def test_email_must_be_valid(self):
        self.form_input['email'] = 'johndoe'
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['email'][0], 'Enter a valid email address.')
        self.form_input['email'] = 'johndoe@'
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['email'][0], 'Enter a valid email address.')
        self.form_input['email'] = 'johndoe@gmail'
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['email'][0], 'Enter a valid email address.')
    
    def test_line_1_must_not_be_empty(self):
        self.form_input['line_1'] = ''
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['line_1'][0], 'This field is required.')
    
    def test_line_2_can_be_empty(self):
        self.form_input['line_2'] = ''
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_amount_can_be_empty(self):
        self.form_input['amount'] = ''
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_city_town_must_not_be_empty(self):
        self.form_input['city_town'] = ''
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['city_town'][0], 'This field is required.')
    
    def test_postcode_must_not_be_empty(self):
        self.form_input['postcode'] = ''
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['postcode'][0], 'This field is required.')
    
    def test_country_must_not_be_empty(self):
        self.form_input['country'] = ''
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['country'][0], 'This field is required.')
    
    def test_amount_initial_value(self):
        initial_data = {
            'amount': self.cart.total_price
        }
        form = CheckoutForm(initial=initial_data)
        expected_amount = initial_data['amount']
        actual_amount = form.fields['amount'].initial
        self.assertEqual(actual_amount, expected_amount)
    
    def test_no_initial_amount_value(self):
        form = CheckoutForm(initial={})
        self.assertIsNone(form.fields['amount'].initial)
    
    def test_amount_invalid_value(self):
        self.form_input['amount'] = 'invalid_amount'
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['amount'][0], 'Enter a number.')

    def test_form_labels(self):
        form = CheckoutForm()
        form_html = form.as_p()
        expected_label_full_name = self._render_label(form, 'full_name', 'Full name')
        expected_label_email = self._render_label(form, 'email', 'Email')
        expected_label_line_1 = self._render_label(form, 'line_1', 'Address line 1')
        expected_label_line_2 = self._render_label(form, 'line_2', 'Address line 2')
        expected_label_city_town = self._render_label(form, 'city_town', 'City/Town')
        expected_label_postcode = self._render_label(form, 'postcode', 'Postcode')
        expected_label_country = self._render_label(form, 'country', 'Country')
        self.assertIn(expected_label_full_name, form_html)
        self.assertIn(expected_label_email, form_html)
        self.assertIn(expected_label_line_1, form_html)
        self.assertIn(expected_label_line_2, form_html)
        self.assertIn(expected_label_city_town, form_html)
        self.assertIn(expected_label_postcode, form_html)
        self.assertIn(expected_label_country, form_html)
    
    def _render_label(self, form, field_name, label):
        return f'<label for="{form[field_name].auto_id}">{label}:</label>'
        