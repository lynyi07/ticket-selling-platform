from django.shortcuts import render, redirect
from ..forms.login_form import LogInForm
from django.contrib.auth import login
from django.views import View
from django.utils.decorators import method_decorator
from tsp.views.helpers import login_prohibited
from django.contrib import messages

class LogInView(View):
    """View for users to login."""

    http_method_names = ['get', 'post']

    @method_decorator(login_prohibited)
    def dispatch(self, request):
        return super().dispatch(request)

    def get(self, request):
        """
        Handle the GET request to the login view.
        
        Returns
        -------
        HttpResponse
            A response to the login page.
        """

        return self.render()

    def post(self, request):
        """
        Handle and validate the POST request to log in a user.

        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.

        Returns
        -------
        HttpResponse or HttpRedirect
            If the user is authenticated, redirect to the user's edit profile 
            page.
            if they are a society, otherwise redirect to the landing page.
            If the user is not authenticated, render the login form with an 
            error message.
        """

        form = LogInForm(request.POST)
        user = form.get_user()
        if user is not None:
            if user.role != request.POST.get('account'):
                messages.add_message(request, messages.INFO, "Wrong account type!")
                return self.render()
            login(request, user)
            if user.role == 'SOCIETY':
                return redirect('/edit_profile_page/')
            else:
                return redirect('landing')
        messages.add_message(request, messages.INFO, "Invalid credentials!")
        return self.render()

    def render(self):
        """Render login template with blank form"""

        form = LogInForm()
        return render(self.request, 'login.html', {'form':form})