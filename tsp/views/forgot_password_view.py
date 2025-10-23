from django.shortcuts import render, redirect
from ..models import User
from ..forms.forgot_password_form import ForgetPasswordForm 
from ..views.change_password_view import ChangePasswordMixin
from django.views import View
from tsp.views.helpers import login_prohibited, send_email, send_message
from django.utils.decorators import method_decorator
from django.contrib import messages

class ForgetPasswordView(View):  
    """View for users that forgot their password."""

    @method_decorator(login_prohibited)
    def dispatch(self, request):
        return super().dispatch(request)

    def get(self, request):
        """
        Handle the GET request to the forgot password view.

        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.

        Returns
        -------
        HttpResponse
            A response to the forgot password page.
        """
        return self.render() 

    def post(self, request):
        """
        Handle and validate the POST request to the forgot password view.

        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.

        Returns
        -------
        HttpResponse
            A response to the change password page.
        """

        form = ForgetPasswordForm(request.POST) 
        email = form.get_email() 
        if email is not None:  
            if self.check_user_in_database(email): 
                id = User.objects.get(email=email).pk
                message = send_message(request, id, 'email/forgot_password_email.html')  
                send_email(request, [email], 'Password Reset Request', message)
                messages.add_message(
                    request, 
                    messages.SUCCESS, 
                    "Email has been sent to your inbox!"
                )
                return redirect('forgot_password')
        messages.add_message(request, messages.INFO, "Email does not exist!")
        return self.render() 

    def check_user_in_database(self, user_email):
        """
        Handle check to make sure email is signed up with system.
        
        Returns
        -------
        bool
            True if email exists in the system.
        """
        if User.objects.filter(email=user_email).exists():
            return True 
        return False

    def render(self): 
        """Render forgot password template with blank form."""
        
        form = ForgetPasswordForm() 
        return render(self.request, 'forgot_password.html', {'form':form})    

class ChangePassword(ChangePasswordMixin, View): 
    """View for users to change their password when forgetting password."""

    http_method_names = ['get', 'post']

    def dispatch(self, request, uidb64):
        return super().dispatch(request, uidb64)
