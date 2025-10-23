from django.views.generic.edit import UpdateView
from tsp.models import Society
from tsp.forms.society.member_fee_form import MemberFeeForm
from django.contrib import messages
from django.shortcuts import redirect
from tsp.views.helpers import SocietyAccessMixin

class MemberFeeView(SocietyAccessMixin, UpdateView):
    """View that updates the annual member fee for a society."""

    model = Society
    form_class = MemberFeeForm
    template_name = 'society/member_fee.html'
    
    def get_object(self):
        """
        Get the current society.

        Returns
        -------
        Society
            The current society user.
        """
        
        return self.request.user.society

    def form_valid(self, form):
        """
        Check if the form value is valid and update the member fee 
        accordingly.

        Parameters
        ----------
        form : MemberFeeForm
            The member fee form object.

        Returns
        -------
        HttpResponseRedirect
            A redirect response to the member fee page.
        """

        form.save()
        messages.success(self.request, "Member fee updated successfully!")
        return redirect(self.request.path_info)
