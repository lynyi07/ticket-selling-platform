from tsp.views.helpers import SocietyAccessMixin
from django.views.generic import ListView
from tsp.models import Society

class ListRegularMembers(SocietyAccessMixin, ListView):
    """View that displays a list of regular members for a society account.""" 
    
    model = Society 
    template_name = 'society/regular_members_list.html'
    context_object_name = "users"
    
    def get_queryset(self):
        """
        Get the queryset of regular members in the society.

        Returns
        -------
        queryset
            The queryset of regular members to be displayed in the view that 
            is filtered based on the society account logged in. 
        """

        society = self.request.user.society
        regular_members = society.regular_members.order_by('first_name')
        return regular_members