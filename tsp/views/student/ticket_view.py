from django.views.generic import DetailView
from tsp.views.helpers import StudentAccessMixin
from tsp.models import Ticket, Order

class TicketView(StudentAccessMixin, DetailView):
    """View to display all tickets for an order of the current student."""
    
    model = Order
    template_name = 'student/tickets.html'
    context_object_name = 'tickets'

    def get_context_data(self, **kwargs):
        """
        Get the context data to be used in rendering the template.
        
        Returns
        -------
        dict
            A dictionary containing the following key(s):
            - 'tickets': The tickets from an order.
        """
        
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context['tickets'] = Ticket.objects.filter(order=order)
        return context

    def get_queryset(self):
        """Get the queryset of Ticket objects filtered by the currently 
        authenticated student.
        
        Returns
        -------
        QuerySet
            The queryset of Ticket objects associated with the currently 
            authenticated student.
        """
        
        queryset = super().get_queryset()
        return queryset.filter(student=self.request.user.student)