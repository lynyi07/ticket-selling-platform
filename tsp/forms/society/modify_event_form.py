from django.db import IntegrityError
from django import forms
from tsp.models import Event
from tsp.forms.society.base_event_form import BaseEventForm

class ModifyEventForm(BaseEventForm):
    """Form to modify an event."""

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with event instance.
        If the event instance exists, set the form field values with the 
        corresponding values from the event instance.
        """
        
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
            
        # Make price field and early_booking_capacity field read-only
        self.fields['early_bird_price'].widget = forms.TextInput(
            attrs={'readonly': True}
        )
        self.fields['standard_price'].widget = forms.TextInput(
            attrs={'readonly': True}
        )
        self.fields['early_booking_capacity'].widget = forms.TextInput(
            attrs={'readonly': True}
        )
        
    def setup_initials(self, event_id: int) -> None:
        """
        Populates the inputs with the appropriate event data.
        
        Parameters
        ----------
        event_id: int
            ID of the event to populate its data with.
        """
        
        event: Event = Event.objects.get(pk=event_id)
        self.event = event
        self.fields['name'].initial = event.name
        self.fields['description'].initial = event.description
        self.fields['location'].initial = event.location
        self.fields['photo'].initial = event.photo
        self.fields['start_time'].initial = event.start_time
        self.fields['end_time'].initial = event.end_time
        self.fields['early_booking_capacity'].initial = event.early_booking_capacity
        self.fields['standard_booking_capacity'].initial = event.standard_booking_capacity
        self.fields['early_bird_price'].initial = event.early_bird_price
        self.fields['standard_price'].initial = event.standard_price
        
    def clean(self):
        """
        Clean the data and generate messages for any errors.
        
        A socity can not decrease the regular booking capacity of an existing 
        event.

        Returns:
        -------
        dict
            The cleaned form data.
        """
        
        cleaned_data = super().clean()
        standard_booking_capacity = self.cleaned_data.get('standard_booking_capacity')
        name = self.cleaned_data.get('name')
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        
        if self.event:
            original_capacity = self.event.standard_booking_capacity
            if standard_booking_capacity < original_capacity:
                self.add_error(
                    'standard_booking_capacity', 
                    "You can not decrease regular booking capacity."
                )
            
            existing_events = Event.objects.filter(
                name=name,
                start_time=start_time,
                end_time=end_time
            ).exclude(id=self.event.id)
            super().clean_duplicate_events(existing_events)
            
        return cleaned_data

    def save_modifications(self, event_id):
        """
        Saves the desired modifications entered by the society user in the form.
        
        Parameters
        ----------
        event_id: int
            id of the event to modify.
        """
        
        event: Event = Event.objects.get(pk=event_id)
        original_photo = event.photo
        
        if self.is_valid():
            event.name = self.cleaned_data.get('name')
            event.description = self.cleaned_data.get('description')
            event.location = self.cleaned_data.get('location')
            event.start_time = self.cleaned_data.get('start_time')
            event.end_time = self.cleaned_data.get('end_time')
            event.early_bird_price = self.cleaned_data.get('early_bird_price')
            event.standard_price = self.cleaned_data.get('standard_price')
            event.early_booking_capacity = self.cleaned_data.get('early_booking_capacity')
            event.standard_booking_capacity = self.cleaned_data.get('standard_booking_capacity')
            
            # Set the event photo.
            if self.cleaned_data.get('photo'):
                # Update event photo if a new photo is uploaded.
                event.photo = self.cleaned_data.get('photo')
            elif original_photo:
                event.photo = original_photo          
            else: 
                event.photo = 'static/images/default_event_photo.jpg'
            
            # Save the modified event instance and only update the specified fields
            try:
                event.save(
                    update_fields=[
                        'name', 'description', 'location', 'start_time', 
                        'end_time', 'early_bird_price', 'standard_price', 
                        'early_booking_capacity', 'standard_booking_capacity', 
                        'photo'
                    ]
                )
            except IntegrityError as e:
                raise ValueError(
                    "Failed to save changes to event: {}".format(str(e))
                )