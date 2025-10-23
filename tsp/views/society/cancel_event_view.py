from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from tsp.models import Event
from tsp.views.helpers import SocietyAccessMixin, send_email, send_event_message
from django.views import View
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages

class CancelEventView(SocietyAccessMixin, View):
    """View for societies to cancel an event."""

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to the cancel event view.

        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.

        Returns
        -------
        HttpResponseRedirect
            A redirect response to the events list page.
        """
        
        event_id = request.POST.get('event_id')
        event = get_object_or_404(Event, id=event_id)
        event.cancel_event()
        event.save()
        self._generate_cancel_emails(request, event)
        return redirect('events_list')
    
    def _generate_cancel_emails(self, request, event):
        """
        Generate the cancellation email for all of the students who bought 
        the ticket or saved the event.
        If a student both saved the event and bought ticket(s), he/she is 
        recognized as a buyer.

        Parameters
        ----------
        request : HttpRequest
            The current HTTP request.
        event : Event
            The cancelled event.
        """

        email_to_buyer = 'society/email/cancel_event_email_buyer.html'
        email_to_saver = 'society/email/cancel_event_email_saver.html'
        
        try:
            for buyer in event.event_buyers:
                self._send_cancel_email(request, event, buyer, email_to_buyer)
            for saver in event.event_filtered_savers:
                self._send_cancel_email(request, event, saver, email_to_saver)
            messages.success(request, 'Cancellation emails sent successfully!')
        except Exception as e:
            messages.error(request, 'Failed to send the cancellation emails.')

    def _send_cancel_email(self, request, event, user, email_template):
        """
        Send a cancellation email to a user for a cancelled event.
        
        Parameters
        ----------
        request : HttpRequest
            The current HTTP request.
        event : Event
            The cancelled event.
        user : User
            The user who bought the ticket or saved the event.
        email_template : str
            The path to the email template to use for the email.
        
        Returns
        -------
        bool
            True if the email was successfully sent, False otherwise.
        """
    
        mail_subject = 'We\'re sorry, the event ' + event.name + ' is cancelled!'
        message = send_event_message(request, user, event, email_template)  
        send_email(request, [user.email] , mail_subject, message)