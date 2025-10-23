from django.views.generic.edit import UpdateView
from tsp.models import Society
from tsp.forms.society.member_discount_form import MemberDiscountForm
from django.contrib import messages
from django.shortcuts import redirect
from tsp.views.helpers import SocietyAccessMixin

class MemberDiscountView(SocietyAccessMixin, UpdateView):
    """View that updates the member discount percentage for a society."""

    model = Society
    form_class = MemberDiscountForm
    template_name = 'society/member_discount.html'
    success_url = '/member_discount/'
    
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
        Check if the form value is valid and update the member discount 
        percentage accordingly.

        Parameters
        ----------
        form : MemberDiscountForm
            The member discount form object.

        Returns
        -------
        HttpResponseRedirect
            A redirect response to the member discount page.
        """
        
        form.save()
        messages.success(
            self.request, 
            "Member discount updated successfully!"
        )
        return super().form_valid(form)