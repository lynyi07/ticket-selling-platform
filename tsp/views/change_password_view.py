from django.shortcuts import render, redirect
from ..models import User
from ..forms.change_password_form import ChangePasswordForm
from django.contrib.auth import login
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

class ChangePasswordMixin:
    """Mixin for views that handle changing a user's password."""

    form_class = ChangePasswordForm
    template_name = 'change_password.html'
    
    def get(self, request, uidb64=None):
        """
        Handle the GET request to the change password view.

        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.
        uidb64 : String, optional
            The user id in base 64 format. Default is None.

        Returns
        -------
        HttpResponse
            A response to the change password page.
        """
        
        form = ChangePasswordForm() 
        return self.render(form)
    
    def post(self, request, uidb64=None):
        """
        Handle and validate the POST request to the change password view.

        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.
        uidb64 : String, optional
            The user id in base 64 format. Default is None.

        Returns
        -------
        HttpResponse or HttpRedirect
            A http response to the change password page if the form is invalid.
            Otherwise redirect user if the password is updated.
        """

        form = self.form_class(request.POST)
        user = None
        if uidb64:
            # If a uidb64 parameter is provided in the URL, decode it and get 
            # the corresponding user object
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
        else:
            # If no uidb64 parameter is provided in the URL, use the current 
            # authenticated user
            user = request.user

        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            login(request, user)
            messages.add_message(request, messages.SUCCESS, "Password updated!")
            return redirect('change_password')
        # Reload the form if it is invalid
        return self.render(form)
    
    def render(self, form):
        """
        Render the change password template with the given form.

        Parameters
        ----------
        form : forms.Form
            The change password form instance to be rendered.

        Returns
        -------
        HttpResponse
            The rendered change password template response.
        """

        return render(self.request, self.template_name, {'form': form})
    
class ChangePasswordView(ChangePasswordMixin, View):
    """View for users to change their password."""

    http_method_names = ['get', 'post']

    @method_decorator(login_required)
    def dispatch(self, request):
        return super().dispatch(request)