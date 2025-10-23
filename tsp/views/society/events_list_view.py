from django.views.generic import ListView
from tsp.models import Event, Society
from tsp.views.helpers import SocietyAccessMixin

class EventListView(SocietyAccessMixin, ListView):
    """View that displays a list events for a society account."""

    model = Event
    template_name = 'society/events_list.html'
    selected_option = "UPCOMING"
    options = [
        ("UPCOMING", "Upcoming events"), 
        ("PAST", "Past events"), 
        ("CANCELLED", "Cancelled events")
    ]

    def get_queryset(self):
        """
        Get the queryset of events for the society.

        Returns
        -------
        queryset
            The queryset of events to be displayed in the view that is 
            filtered based on the value of user selection.
            Upcoming events are displayed if event type is not selected.
        """
        
        user = self.request.user
        society = Society.objects.get(pk=user.pk)
        event_type = self.request.GET.get('event_type', self.selected_option)
        self.selected_option = event_type
        
        if event_type == 'PAST':
            queryset = society.past_events
        elif event_type == 'CANCELLED':
            queryset = society.cancelled_events
        elif event_type == 'UPCOMING':
            queryset = society.upcoming_events
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                society__in=[society], 
                name__icontains=search_query
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Get the data to be used in the template.

        Returns
        -------
        dict
            A dictionary containing the following key(s):
            - 'options': A list of options for filtering.
            - 'selected_option': The selected option.
            - 'search': The input from the user to search events.
        """

        context = super().get_context_data(**kwargs)
        context["options"] = self.options
        context["selected_option"] = self.selected_option
        context["search"] = self.request.GET.get('search', '')
        return context