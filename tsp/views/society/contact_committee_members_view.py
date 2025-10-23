from django.shortcuts import render
from django.views import View
from tsp.views.helpers import send_email
from django.contrib import messages
from tsp.views.helpers import SocietyAccessMixin
from tsp.forms.society.contact_members_form import ContactCommitteeMembersForm  
from tsp.models import Society

class ContactCommitteeMembersView(SocietyAccessMixin, View):
    """View for users to contact committee members."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """
        Handle the GET request to the contact committee members view.

        Returns
        -------
        HttpResponse
            Render contact committee members template with blank form.
        """

        return self.render()

    def post(self, request):
        """
        Handle the POST request to the contact committee members view.

        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.

        Returns
        -------
        HttpResponse
            Render contact committee members template with blank form.
        """
        
        form = ContactCommitteeMembersForm(request.POST)
        if form.is_valid(): 
            mail_subject = form.get_header() 
            mail_message = form.get_message()  
            society = Society.objects.get(pk=request.user.pk)
            committee_members = society.committee_members
            emails = []
            for member in committee_members: 
                emails.append(member.email)
            send_email(request, emails, mail_subject, mail_message)
            messages.success(request, 'Email sent successfully!')
        return self.render()

    def render(self):
        """
        Render contact committee members template with blank form.
        
        Returns
        -------
        HttpResponse
            Render contact committee members template with blank form.
        """

        form = ContactCommitteeMembersForm()
        return render(self.request, 'society/contact_committee_members.html', {'form':form}) 