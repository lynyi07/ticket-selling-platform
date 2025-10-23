from django.views.generic import ListView
from django.db.models import Q
from tsp.models import Society, University
from tsp.views.helpers import StudentAccessMixin

class AllSocietiesView(StudentAccessMixin, ListView):
    """View that displays a list of all societies."""

    model = Society
    template_name = 'student/all_societies.html'

    def get_queryset(self):
        """
        Get the queryset of societies.

        Returns
        -------
        queryset
            All societies belonging to the same university as the user, 
            filtered by the search query and ordered by name.
        """
        
        search_query = self.request.GET.get('search', "")
        return Society.objects.filter(
            name__icontains=search_query,
            university=self.request.user.university,
        ).order_by('name')

    def get_context_data(self, **kwargs):
        """
        Get the data to be used in the template.

        Returns
        -------
        context : dict
            A dictionary containing the following key(s):
            - 'search': The search query input from the user to filter events.
        """

        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', "")
        context['search'] = search_query
        return context