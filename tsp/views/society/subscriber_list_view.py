from tsp.views.helpers import SocietyAccessMixin
from django.views.generic import ListView
from tsp.models import Society

class SubscriberListView(SocietyAccessMixin, ListView):
    """View that displays a list of subscribers for a society account."""   

    model = Society 
    template_name = 'society/subscribers_list.html'
    context_object_name = "users"

    def get_queryset(self):
        """
        Get the queryset of students subscribing a society's emailing list.

        Returns
        -------
        queryset
            The queryset of students to be displayed in the view
            that is filtered based on the society account logged in. 
        """
        
        society = self.request.user.society
        subscribers = society.subscribers.order_by('first_name')
        return subscribers
   