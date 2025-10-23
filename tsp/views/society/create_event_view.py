from tsp.views.helpers import SocietyAccessMixin, send_email, send_event_message
from django import forms
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from tsp.models import Event, Society
from tsp.forms.society.create_event_form import CreateEventForm
from django.shortcuts import get_object_or_404

class CreateEventView(SocietyAccessMixin, CreateView):
    """View that creates an event."""

    model = Event
    form_class = CreateEventForm
    template_name = 'society/create_event.html'
    success_url = reverse_lazy('create_event')
    success_message = 'Event created successfully!'

    def form_valid(self, form):
        """
        Handle the valid form submission.

        Save the new event object and add it to the associated societies
        before redirecting to the event detail page.

        Parameters
        ----------
        form : CreateEventForm
            The form instance containing the valid data.

        Returns
        -------
        HttpResponseRedirect
            The HTTP response object that represents the redirect to the 
            event detail page.
        """

        # Get the partner societies of the event
        try:
            partner_societies = form.clean_partners()    
        except forms.ValidationError as e:
            return self.form_invalid(form)
        
        # Add the partner societies to the event
        event = form.save()
        if partner_societies:
            for partner in partner_societies:
                event.society.add(partner.id)

        # Set the host and add it to event if the society has set bank details.
        host = self.request.user.society
        if host and not host.has_bank_details:
            event.delete()
            messages.error(self.request, "Host does not have bank details.")
            return self.form_invalid(form)
        event.host = self.request.user.society
        event.society.add(event.host.id) 

        # Set the event photo and save the event
        if self.request.FILES.get('photo'):
            event.photo = self.request.FILES.get('photo')
        event.save()
  
        # Send email about created event to subscribers
        self._send_event_notification(event)

        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Handle error when the form is submitted with invalid data.

        Parameters
        ----------
        form : CreateEventForm
            The form instance containing the invalid data.

        Returns
        -------
        HttpResponse
            Render the invalid form.    
        """
        
        messages.error(self.request, 'Failed to create event.')
        return super().form_invalid(form)
    
    def _send_event_notification(self, event):
        """
        Send an event notification to subscribed users.

        Parameters
        ----------
        event : Event
            The event that has been created
        """

        subscribers = event.host.subscriber.all()
        for society in event.society.all():
            subscribers |= society.subscriber.all()

        for subscriber in subscribers.distinct():
            message = send_event_message(self.request, subscriber, event, 'society/email/create_event_email.html')  
            send_email(self.request, [subscriber.email], f'{event.host.name} has created a new event!', message)