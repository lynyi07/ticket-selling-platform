from django.urls import reverse 
from tsp.views.helpers import send_email
from django.test import TestCase 

class LoginTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url 

class EmailTester(TestCase):  
    """Tests regarding any email methods"""

    def test_send_email(self): 
        response = send_email('GET', 'daniel.1.holland@kcl.ac.uk', 'Test Email', 'This is a test') 
        self.assertEqual(response.status_code, 200)  