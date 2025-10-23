from django.utils import timezone
from django import forms
from tsp.models import Event

class BaseEventForm(forms.ModelForm):
    """Base Form to create or modify an event."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the class instance."""

        self.user = kwargs.pop('user', None)
        super(BaseEventForm, self).__init__(*args, **kwargs)
        if self.user:
            self.instance.host = self.user.society
            self.instance.society.add(self.user)

    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput()
    )

    class Meta:
        """Form options."""

        model = Event
        fields = ['name', 'description', 'photo', 'location',
                  'start_time', 'end_time', 'early_booking_capacity',
                  'standard_booking_capacity', 'early_bird_price', 
                  'standard_price']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows':4}),
            'early_booking_capacity': forms.NumberInput(),
            'standard_booking_capacity': forms.NumberInput(),
            'early_bird_price': forms.NumberInput(),
            'standard_price': forms.NumberInput(),
        }

        # Fields to be excluded.
        exclude = ['host', 'society', 'status']

    def clean(self):
        """
        Clean the form data and generate error messages for any validation 
        errors.

        Check if start time is not in the past, end time is after start time, 
        early bird price is less than standard price, prices and booking 
        capacities are non-negative.
        Check if an event with the same name, start time, and end time already 
        exists in the database.

        Returns:
        -------
        dict
            The cleaned form data.
        """

        cleaned_data = super().clean()
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        early_bird_price = self.cleaned_data.get('early_bird_price')
        standard_price = self.cleaned_data.get('standard_price')
        early_booking_capacity = self.cleaned_data.get('early_booking_capacity')
        standard_booking_capacity = self.cleaned_data.get('standard_booking_capacity')
        
        # Validate the form data
        if start_time and start_time < timezone.now():
            self.add_error('start_time', "Start time can't be in the past.")
        if end_time and end_time <= start_time:
            self.add_error('end_time', "End time must be after start time.")
        if early_bird_price and early_bird_price < 0:
            self.add_error('early_bird_price', "This value can't be negative.")
        if standard_price and standard_price < 0:
            self.add_error('standard_price', "This value can't be negative.")
        if early_booking_capacity and early_booking_capacity < 0:
            self.add_error('early_booking_capacity', "This value can't be negative.")
        if standard_booking_capacity and standard_booking_capacity < 0:
            self.add_error('standard_booking_capacity', "This value can't be negative.")
        if ((standard_price and early_bird_price and standard_price <= early_bird_price)
            or (early_bird_price and not standard_price)):
            self.add_error(
                'standard_price', 
                "Standard price must be higher than early bird price."
            )
            
        return cleaned_data
    
    def clean_duplicate_events(self, existing_events):
        """
        Check if any existing events have the same name, start time and end time 
        as the event being created or updated.
        If any duplicates exist, add errors to the form to prevent the creation 
        or modification of the event.

        Parameters
        ----------
        existing_events : queryset
            The queryset containing existing events.
        """
    
        if existing_events.exists():
            self.add_error(
                'name',
                "Event with the same name, start time and end time already exists."
            )
            self.add_error(
                'start_time',
                "Event with the same name, start time and end time already exists."
            )
            self.add_error(
                'end_time',
                "Event with the same name, start time and end time already exists."
            )