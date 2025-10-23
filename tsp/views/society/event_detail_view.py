from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.generic import DetailView
from tsp.models import Event
from tsp.views.helpers import SocietyAccessMixin

class EventDetailView(SocietyAccessMixin, DetailView):
    """View that displays a details of an event.""" 

    model = Event
    template_name = 'society/event_detail.html'
    context_object_name = 'event'
    
    def get_object(self):   
        """
        Get the requested event object and check if it is organised by the 
        current society. Raise a 404 error if the condition is not met.

        Returns
        -------
        Society
            The requested event object if it is organised by the society. 
            
        Raises
        ------
        Http404
            If the event is not organised by the current society.
        """
        
        event = get_object_or_404(Event, pk=self.kwargs.get('pk'))
        society = self.request.user.society
        if not event.is_organiser(society):
            raise Http404
        return event
        
    