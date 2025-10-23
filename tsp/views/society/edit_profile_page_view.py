from tsp.views.helpers import SocietyAccessMixin
from django.views.generic import DetailView
from tsp.models import Society

class EditProfilePageView(SocietyAccessMixin, DetailView):
    """View that displays their profile page to a society account."""   

    model = Society 
    template_name = 'society/edit_profile_page.html'
    context_object_name = "society"
    
    def get_object(self):
        """
        Get the current society.

        Returns
        -------
        Society
            The current society user.
        """
        
        return self.request.user.society