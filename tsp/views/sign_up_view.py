from django.shortcuts import render, redirect
from ..forms.sign_up_form import SignUpForm
from django.contrib.auth import authenticate
from django.views import View 
from django.utils.decorators import method_decorator
from tsp.views.helpers import login_prohibited, send_email
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.contrib import messages
from tsp.models import User

def activate(request, uidb64, token):
    """
    Activate user's account when the user clicks the link in the email.

    Parameters
    -------
    request : HttpRequest
        The HTTP request object.
    uidb64 : object
        The user's id in base 64 format.
    token : String
        The account activation token.

    Returns
    -------
    HttpResponseRedirect
        A redirected response to the login page (if successful).
        A redirected response to the landing page (if not successful).
    """

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login to your account.')
        return redirect('login')
    else:
        messages.error(request, 'Sorry, the activation link is invalid!')
    
    return redirect('sign_up')


def activate_account_email(request, user, user_name, to_email):
    """
    Send an email to verify they are the users themselves.

    Parameters
    -------
    request : HttpRequest
        The HTTP request object.
    user : object
        The user object.
    user_name : String
        The user's name.
    to_email : String
        The user's email.
    """

    mail_subject = 'Activate your user account'
    message = render_to_string('email/activate_account_email.html', {
        'user': user,
        'user_name': user_name,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    is_sent = send_email(request, to_email, mail_subject, message)
    if is_sent:
        messages.success(request, f'Please go to your email ({to_email[0]}) inbox and click on \
        the activation link to complete your registration. \n Note: Check your spam folder!')
    else:
        messages.error(request, f'Sorry, failed to send a confirmation email to {to_email[0]}, \
            please check if it is a correct email address.')


class SignUpView(View):
    """View for users to sign up as a student."""

    http_method_names = ['get', 'post']

    @method_decorator(login_prohibited)
    def dispatch(self, request):
        return super().dispatch(request)

    def get(self, request):
        """
        Handle the GET request to the sign up view.
        
        Returns
        -------
        HttpResponse
            A response to the login page with a blank form.
        """
        
        form = SignUpForm() 
        return self.render(form)
    
    def post(self, request):
        """
        Handle and validate the POST request to the sign up view.
        
        Returns
        -------
        HttpResponse
            A response to the login page with the current form.
        """

        form = SignUpForm(request.POST) 
        if form.is_valid():
            user = form.save()
            new_user = authenticate(email=form.cleaned_data.get('email').lower(), password=form.cleaned_data.get('password'))
            if new_user:
                # Send an email to activate the account
                new_user.is_active=False
                new_user.save()
                activate_account_email(
                    request, 
                    new_user, 
                    user.first_name, 
                    [form.cleaned_data.get('email').lower()]
                )
            return self.render(form)
        # Reload the form if it is invalid
        return self.render(form) 

    def render(self, form): 
        """
        Render the sign up template with the given form.

        Parameters
        ----------
        form : forms.Form
            The sign up form instance to be rendered.

        Returns
        -------
        HttpResponse
            The rendered sign up template response.
        """

        return render(self.request, 'sign_up.html', {'form':form}) 