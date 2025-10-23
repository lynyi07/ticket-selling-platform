from django import forms
from tsp.models import Order

class CheckoutForm(forms.ModelForm):
    """Form to checkout."""
    
    # Add fields to the form
    payment_method_id = forms.CharField(widget=forms.HiddenInput())
    full_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    amount = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    
    def __init__(self, *args, **kwargs):
        """Initialize the class instance."""

        super().__init__(*args, **kwargs)
        
        # Set the value of the `amount` field
        if 'initial' in kwargs:
            initial = kwargs['initial']
            if 'amount' in initial:
                self.fields['amount'].initial = initial['amount']

    class Meta:
        """Form options."""
        
        model = Order
        fields = ['full_name', 'email', 'line_1', 'line_2', 'city_town', 'postcode', 'country', 'payment_method_id']
        widgets = {
            'full_name': forms.TextInput(attrs={'required': 'required'}),
            'email': forms.EmailInput(attrs={'required': 'required'}),
            'line_1': forms.TextInput(attrs={'required': 'required'}),
            'line_2': forms.TextInput(),
            'city_town': forms.TextInput(attrs={'required': 'required'}),
            'postcode': forms.TextInput(attrs={'required': 'required'}),
            'country': forms.TextInput(attrs={'required': 'required'}),
        }
        labels = {
            'full_name': 'Full Name',
            'email': 'Email',
            'line_1': 'Address line 1',
            'line_2': 'Address line 2',
            'city_town': 'City/Town',
            'postcode': 'Postcode',
            'country': 'Country',
        }
    