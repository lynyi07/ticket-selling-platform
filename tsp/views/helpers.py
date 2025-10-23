from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from tsp.models import User
from typing import Union 

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

class BaseAccessMixin(AccessMixin):
    """Base class for access control mixins."""
    
    def check_access(self, request: HttpRequest) -> bool:
        """Check if the user has the required access to view the page."""
        
        return False

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> Union[HttpResponse, HttpResponseRedirect]:        
        if request.user.is_authenticated:
            if self.check_access(request):
                return super().dispatch(request, *args, **kwargs)
            else:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return redirect(f'/{settings.LOGIN_URL}/?next={request.path}')

class StudentAccessMixin(BaseAccessMixin):
    """
    Provides access control for student users in order to restrict views to 
    student only.
    """
    
    def check_access(self, request: HttpRequest) -> bool:
        return request.user.role == User.Role.STUDENT
    
class SocietyAccessMixin(BaseAccessMixin):
    """
    Provides access control for society users in order to restrict views to 
    society only.
    """
    
    def check_access(self, request: HttpRequest) -> bool:
        return request.user.role == User.Role.SOCIETY
    
class StudentUnionAccessMixin(BaseAccessMixin):
    """
    Provides access control for student union users in order to restrict views 
    to student union only.
    """
    
    def check_access(self, request: HttpRequest) -> bool:
        return request.user.role == User.Role.STUDENT_UNION

def login_prohibited(view_function): 
    """
    Decorator that prevents authenticated users from accessing a view. 
    
    Redirect a user to the page specified by the REDIRECT_URL_WHEN_LOGGED_IN 
    setting if the user is already logged in.
    """

    def modified_view_function(request): 
        if request.user.is_authenticated: 
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN) 
        else: 
            return view_function(request) 
    return modified_view_function

def login_required(user_roles): 
    """
    Decorator that prevents certain authenticated users from accessing a view. 
    
    Redirect a user to the page specified by the REDIRECT_URL_WHEN_LOGGED_IN 
    setting if the user is already logged in.
    """

    def wrapper(view_function):
        def modified_view_function(request, *args, **kwargs): 
            if request.user.is_authenticated:
                if request.user.role in user_roles:
                    return view_function(request, *args, **kwargs) 
                else: 
                    return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                return redirect(f'/{settings.LOGIN_URL}/?next={request.path}')
        return modified_view_function
    return wrapper

def send_email(request, to_email, mail_subject, message): 
    """Forms and sends email to user"""

    mail_subject = mail_subject
    message = message
    email = EmailMessage(mail_subject, message, to=to_email)
    if email.send():
        return True
    return False

def send_message(request, user_id, web_format): 
    """Forms message for emails"""

    message = render_to_string(web_format, {
        'domain': get_current_site(request).domain, 
        'uid': urlsafe_base64_encode(force_bytes(user_id)), 
        'protocol': 'https' if request.is_secure() else 'http'
    }) 
    return message

def send_event_message(request, recipient, event, web_format): 
    """Event notification message for emails"""

    message = render_to_string(web_format, {
        'domain': get_current_site(request).domain, 
        'user': recipient,
        'event': event, 
        'protocol': 'https' if request.is_secure() else 'http'
    }) 
    return message