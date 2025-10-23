from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from tsp.models import Society
from tsp.views.helpers import SocietyAccessMixin

class ClearRegularMembersView(SocietyAccessMixin, View):
    """View for societies to remove all regular members."""
    
    def post(self, request, *args, **kwargs):
        """
        Remove all regular members from the society's regular member list.

        Returns
        -------
        HttpResponseRedirect
            Redirect the user to the regular member list page after removing 
            all regular members.
        """
        
        society = request.user.society
        society.regular_member.clear()
        messages.success(request, "All regular members have been removed.")
        return redirect('list_regular_member')