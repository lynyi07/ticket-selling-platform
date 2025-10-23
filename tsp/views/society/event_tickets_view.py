from django.views.generic import ListView
from tsp.views.helpers import SocietyAccessMixin
from tsp.models import Ticket, Event
from django.shortcuts import get_object_or_404, redirect

class EventTicketsView(SocietyAccessMixin, ListView):
    """View that displays a list of tickets for an event."""

    model = Ticket
    template_name = 'society/event_tickets.html'

    def get_queryset(self):
        """
        Get the queryset of all the tickets for the event.

        Returns
        -------
        QuerySet
            The queryset of all the tickets for the event.
        """ 

        event = self.get_object()
        return Ticket.get_tickets_by_event(event)

    def get_object(self):   
        """
        Get the Event object associated with the URL parameter pk.
        
        Returns:
        --------
        Event
            The Event object retrieved based on the URL parameter.
            
        Raises:
        ------
        Http404
            If the object could not be retrieved.
        """
        
        return get_object_or_404(
            Event, 
            pk=self.kwargs.get('pk'),
            society=self.request.user.society
        )