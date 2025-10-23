from django.shortcuts import redirect
from tsp.models import Society, Student 
from tsp.views.helpers import SocietyAccessMixin
from django.views import View

class RemoveCommitteeMemberView(SocietyAccessMixin, View):
    """View for societies to remove a committee member."""
    
    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to the remove committee member view.

        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.

        Returns
        -------
        HttpResponseRedirect
            A redirect response to the committee member list page.
        """
        
        society = request.user.society
        member_pk = request.POST['member_pk']
        member = Student.objects.get(pk=member_pk) 
        society.remove_committee_member(member) 
        return redirect('list_committee_member')