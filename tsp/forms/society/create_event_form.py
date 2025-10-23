from django import forms
from tsp.models import Event, Society
from tsp.forms.society.base_event_form import BaseEventForm

class CreateEventForm(BaseEventForm):
    """Form to create an event."""
    
    partner_emails = forms.CharField(
        label='Partner emails',
        required=False,
        widget=forms.Textarea,
    )
        
    def clean_partners(self):
        """
        Clean and validate the inputted email addresses.

        Returns
        -------
        list
            A list of the corresponded partner societies if all inputted 
            emails are valid. Otherwise raise a validation error.
        """
        
        # Split the string of the inputted emails and remove any extra 
        # whitespaces.
        emails_str = self.cleaned_data.get('partner_emails', '')
        emails = []
        for email_str in emails_str.split(','):
            email = email_str.strip()
            if email:
                emails.append(email)
        partners = []
        invalid_emails = []
        for email in emails:
            try:
                partner = Society.objects.get(email=email)
                if partner:
                    partners.append(partner)
            except Society.DoesNotExist:
                invalid_emails.append(email)
        if invalid_emails:
            # Format the list of invalid emails to a string that is 
            # separated by comma.
            error_msg = f"The following email addresses are invalid: {', '.join(invalid_emails)}"
            self.add_error('partner_emails', error_msg)
            raise forms.ValidationError(error_msg)
        return partners
        
    def clean(self):
        """
        Clean the form data and generate error messages for any validation 
        errors.

        Returns:
        -------
        dict
            The cleaned form data.
        """
        
        cleaned_data = super().clean()

        # Check if duplicated event exists
        name = self.cleaned_data.get('name')
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        existing_events = Event.objects.filter(
            name=name,
            start_time=start_time,
            end_time=end_time
        )
        super().clean_duplicate_events(existing_events)
        return cleaned_data 
        
    def save(self, commit=True):
        """
        Save the form data to the database as a new event.
        
        If a photo has been uploaded, set it as the event's photo.
        Otherwise, set the default event photo.

        Returns:
        -------
        event
            The newly created event.
        """
        
        event = super().save(commit=False)            
        if self.cleaned_data.get('photo'):
            event.photo = self.cleaned_data.get('photo')
        else:
            event.photo = 'static/images/default_event_photo.jpg'
        if commit:
            event.save()
        return event