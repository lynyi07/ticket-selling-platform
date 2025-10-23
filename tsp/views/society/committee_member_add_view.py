from tsp.views.helpers import SocietyAccessMixin
from django.views.generic import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from tsp.models import Society
from tsp.forms.society.add_committee_member_form import AddCommitteeMemberForm

class AddCommitteeMemberView(SocietyAccessMixin, FormView):
    """View to add a committee member to a society."""

    model = Society
    form_class = AddCommitteeMemberForm
    template_name = 'society/committee_member_add.html'
    success_url = reverse_lazy('add_committee_member')
    
    def get_form_kwargs(self):
        """
        Get the keyword arguments for instantiating the add committee member 
        form.

        Returns
        -------
        dict
            The keyword arguments for the form, including the current society.
        """
    
        kwargs = super().get_form_kwargs()
        kwargs['society'] = self.request.user.society
        return kwargs

    def form_valid(self, form):
        """
        If the form is valid, add a new committee member to the society and 
        redirect to the success URL.

        Parameters:
        -----------
        form : AddCommitteeMemberForm
            The form containing the email address of the committee member 
            to add.

        Returns:
        --------
        HttpResponseRedirect
            A redirect response to the success URL along with a success
            message.
        """

        student = form.cleaned_data['student']
        society = Society.objects.get(pk=self.request.user.pk)
        society.add_committee_member(student)
        messages.success(self.request, "New committee member added!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Handle error when the form is submitted with invalid data.

        Parameters
        ----------
        form : AddCommitteeMemberForm
            The form containing the invalid data.

        Returns
        -------
        HttpResponse
            A response that renders the invalid form along with an 
            error message.
        """

        messages.error(self.request, 'Failed to add committee member.')
        return super().form_invalid(form)
