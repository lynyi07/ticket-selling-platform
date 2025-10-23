from django.contrib import messages
from django.http import Http404
from django.urls import reverse_lazy
from tsp.views.helpers import SocietyAccessMixin, send_email, send_event_message
from django.views.generic import UpdateView
from django.shortcuts import render, redirect, reverse
from tsp.models import Event
from tsp.forms.society.modify_event_form import ModifyEventForm
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

class ModifyEventView(SocietyAccessMixin, UpdateView):
    """View that allows societies to modify an event."""

    model = Event
    form_class = ModifyEventForm
    template_name = 'society/modify_event.html'
    success_url = reverse_lazy('modify_event')

    def get(self, request, *args, **kwargs):
        """
        Handle the GET request for the modify event view.

        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.

        Returns
        -------
        HttpResponse
            A response to the modify event page.  
        HttpResponseRedirect
            A redirect response to the events list page if the event is not 
            active, or if the user attempts to access an event that is not 
            organized by own society.
        """

        event = Event.objects.get(pk=self.kwargs['pk'])
        society = request.user.society
        if not event.is_active or not event.is_organiser(society):
            raise Http404()
        form = self.form_class()
        form.setup_initials(self.kwargs['pk'])
        return render(request, self.template_name, {'form': form})
        
    def post(self, request, *args, **kwargs):
        """
        Handle the POST request for the modify event view.
        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.
        Returns
        -------
        HttpResponse
            A response to the modify event page if the form is invalid.
        HttpResponseRedirect
            A redirect to the event detail page if the form is valid.
        """
        
        event = Event.objects.get(pk=self.kwargs['pk'])
        form = self.form_class(request.POST or None, request.FILES or None, event=event)
        if form.is_valid():
            form.save_modifications(self.kwargs['pk'])
            self._generate_emails(request, event)
            return redirect(reverse('event_detail', kwargs={'pk': event.pk}))
        else:
            messages.error(self.request, 'Failed to modify event.')
            context = {
                'form': form,
                'event': event
            }
        return render(request, self.template_name, context)

    def _generate_emails(self, request, event):
        """
        Generate the email for all of the students who bought the ticket or 
        saved the event.
        If a student both saved the event and bought ticket(s), he/she is 
        recognized as a buyer.

        Parameters
        ----------
        request : HttpRequest
            The current HTTP request.
        event : Event
            The cancelled event.
        """

        email_to_buyer = 'society/email/modify_event_email_buyer.html'
        email_to_saver = 'society/email/modify_event_email_saver.html'
        
        try:
            for buyer in event.event_buyers:
                self._send_email(request, event, buyer, email_to_buyer)
            for saver in event.event_filtered_savers:
                self._send_email(request, event, saver, email_to_saver)
            messages.success(request, 'Modification emails sent successfully!')
        except Exception as e:
            print(e)
            messages.error(request, 'Failed to send the modification emails.')

    def _send_email(self, request, event, user, email_template):
        """
        Send the email to a user for a modified event.
        
        Parameters
        ----------
        request : HttpRequest
            The current HTTP request.
        event : Event
            The modified event.
        user : User
            The user who bought the ticket or saved the event.
        email_template : str
            The path to the email template to use for the email.
        
        Returns
        -------
        bool
            True if the email was successfully sent, False otherwise.
        """
        
        mail_subject = 'Changes to ' + event.name 
        message = send_event_message(request, user, event, email_template)  
        send_email(request, [user.email] , mail_subject, message)