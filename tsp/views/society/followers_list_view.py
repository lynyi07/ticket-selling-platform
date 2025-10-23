from tsp.views.helpers import SocietyAccessMixin
from django.views.generic import ListView
from tsp.models import Society

class FollowersListView(SocietyAccessMixin, ListView):
    """View that displays a list of followers for a society account."""   

    model = Society 
    template_name = 'society/followers_list.html'
    context_object_name = "users"

    def get_queryset(self):
        """
        Get the queryset of students following a society.

        Returns
        -------
        queryset
            The queryset of students to be displayed in the view
            that is filtered based on the society account logged in. 
        """
        
        society = self.request.user.society
        followers = society.followers.order_by('first_name')
        return followers
   