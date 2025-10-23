from django.shortcuts import render 
from django.views import View

class LandingPageView(View):
    """View for the landing page."""

    http_method_names = ['get']

    def dispatch(self, request):
        return super().dispatch(request)

    def get(self, request):
        """
        Handle the GET request to the landing page view.
        
        Returns
        -------
        HttpResponse
            A response to the landing page.
        """

        return render(request, 'landing.html')