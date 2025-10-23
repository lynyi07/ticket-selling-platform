from django.views.generic import ListView
from django.utils import timezone
from tsp.models import Event
from tsp.views.helpers import StudentAccessMixin

class AllEventsView(StudentAccessMixin, ListView):
    """View that displays a list of all events."""

    model = Event
    template_name = 'student/all_events.html'
    selected_date_option = "EARLIEST"
    selected_status_option = "UPCOMING"
    date_options = [("EARLIEST", "Earliest"), ("LATEST", "Latest")]
    status_options = [("UPCOMING", "Upcoming"), ("PAST", "Past"), ("CANCELLED", "Cancelled")]
    
    def get_queryset(self):
        """
        Get the queryset of events.

        Returns
        -------
        queryset
            The queryset is filtered based on the value of user selection.
        """   
        
        search_query = self.request.GET.get('search', "")
        date_filter = self.request.GET.get('date_filter', self.selected_date_option)
        self.selected_date_option = date_filter
        status_filter = self.request.GET.get('status_filter', self.selected_status_option)
        self.selected_status_option = status_filter
        context = Event.objects.filter(name__icontains=search_query, society__university=self.request.user.university)
        context = self._filter_by_status(status_filter, context)
        context = self._filter_by_datetime(date_filter, context)
        return context.distinct()
    
    def _filter_by_status(self, status_filter, context):
        """
        Filter the queryset of events based on the status selected by the user.

        Parameters
        ----------
        status_filter : str
            The status to filter events by.
        context : QuerySet
            The queryset of events to filter.

        Returns
        -------
        QuerySet
            The filtered queryset of events.
        """
        now = timezone.now()
        if status_filter == 'UPCOMING':
            context = context.filter(end_time__gte=now, status='ACTIVE')
        elif status_filter == 'PAST':
            context = context.filter(end_time__lt=now, status='ACTIVE')
        elif status_filter == 'CANCELLED':
            context = context.filter(end_time__gte=now, status='CANCELLED')
        return context
    
    def _filter_by_datetime(self, date_filter, context):
        """
        Filter the queryset of events by the earliest or latest start date 
        and time.

        Parameters
        ----------
        date_filter : str
            The selected date and time filter: either 'EARLIEST' or 'LATEST'.
        context : QuerySet
            The queryset of events to filter.

        Returns
        -------
        QuerySet
            The filtered queryset of events.
        """
        
        if date_filter == 'EARLIEST':
            context = context.order_by(
                'start_time__date', 
                'start_time__hour', 
                'start_time__minute'
            )
        elif date_filter == 'LATEST':
            context = context.order_by(
                '-start_time__date', 
                '-start_time__hour', 
                '-start_time__minute'
            )
        return context

    def get_context_data(self, **kwargs):
        """
        Get the data to be used in the template.

        Returns
        -------
        context : dict
            A dictionary containing the following key(s):
            - 'search': The input from the user to search events.
            - 'date_options': A list of date options for filtering.
            - 'status_options': A list of status options for filtering.
            - 'selected_date_option': The selected date option.
            - 'selected_status_option': The selected status option.
        """

        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', "")
        context['date_options'] = self.date_options
        context['status_options'] = self.status_options
        context['selected_date_option'] = self.selected_date_option
        context['selected_status_option'] = self.selected_status_option
        return context