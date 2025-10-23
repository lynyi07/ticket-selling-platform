from django.views.generic import ListView
from django.db.models import Q
from django.utils import timezone
from tsp.models import Society, Event, Student
from tsp.views.helpers import StudentAccessMixin
from itertools import chain

class ForYouPageView(StudentAccessMixin, ListView):
    """View that displays all the events associated with a followed society."""

    model = Event
    template_name = 'student/for_you_page.html'
    selected_society = 'ALL'
        
    def get_queryset(self):
        """
        Get the queryset of events.

        Returns
        -------
        queryset
            The queryset is filtered based on the value of user selection.
        """   
        
        society_filter = self.request.GET.get(
            'society_filter', 
            self.selected_society
        )
        if society_filter != 'ALL':
            self.selected_society = Society.objects.get(name=society_filter)
            context = Event.objects.filter(society=self.selected_society)
        else:
            student = Student.objects.get(id=self.request.user.id)
            followed_societies = Society.objects.filter(follower=student)
            followed_society_events = Event.objects.filter(society__in=followed_societies)
            saved_events = student.saved_event.all()
            context = followed_society_events | saved_events
        context = self._filter_events(context)
        return context

    def _filter_events(self, events):
        """
        Filter a queryset of events based on user selection.
        The queryset is then ordered by start time in ascending order.

        Parameters
        ----------
        events : queryset
            A queryset of events to filter.

        Returns
        -------
        queryset
            The filtered queryset of events.        
        """
    
        search_query = self.request.GET.get('search', "")
        events = events.filter(
            Q(name__contains=search_query),
            Q(end_time__gte=timezone.now()), 
            Q(status='ACTIVE')
        ).distinct().order_by('start_time__date', 'start_time__hour', 'start_time__minute')
        return events

    def get_context_data(self, **kwargs):
        """
        Get the context data to be used in rendering the template.

        Returns
        -------
        dict
            A dictionary containing the following key(s):
            - 'search': The input from the user to search events.
            - 'followed': The societies that the student follows.
            - 'selected_society': The selected society for filtering.
        """

        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', "")
        context['followed'] = list(chain(['ALL'], Society.objects.filter(follower=self.request.user)))
        context['selected_society'] = self.selected_society
        return context