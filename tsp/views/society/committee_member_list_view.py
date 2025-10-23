from tsp.views.helpers import SocietyAccessMixin
from django.views.generic import ListView
from tsp.models import Society

class ListCommitteeMembersView(SocietyAccessMixin, ListView):
    """View that displays a list of committee members for a society account."""   

    model = Society 
    template_name = 'society/committee_members_list.html'
    context_object_name = "users"

    def get_queryset(self):
        """
        Get the queryset of committee members in the society.

        Returns
        -------
        QuerySet
            A QuerySet of committee members to be displayed in the view
            that is filtered based on the society account logged in. 
        """
        
        society = self.request.user.society
        committee_members = society.committee_members.order_by('first_name')
        return committee_members     