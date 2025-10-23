from django.shortcuts import redirect
from django.contrib.auth import logout
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class LogOutView(View):
    """View for users to log out."""

    http_method_names = ['get']

    @method_decorator(login_required)
    def dispatch(self, request):
        return super().dispatch(request)

    def get(self, request):
        """
        Handle the GET request to the logout view.
        
        Returns
        -------
        HttpResponseRedirect
            A redirected response to the landing page.
        """

        logout(request)
        return redirect('landing')