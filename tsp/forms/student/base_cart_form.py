from django import forms
from django.forms import ModelForm
from tsp.models import EventCartItem, Event, Society, Cart

class BaseCartForm(ModelForm):
    """Base form for adding or updating an item in the cart."""
    
    early_bird_to_add = forms.IntegerField(
        label='Early Bird Tickets', 
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False
    )
    standard_to_add = forms.IntegerField(
        label='Standard Tickets', 
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False
    )
    membership = forms.ModelChoiceField(
        queryset=Society.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        """Initialize the class instance."""
        
        self.user = kwargs.pop('user', None)
        self.event = kwargs.pop('event', None)
        self.cart = None
        self.event_cart_item = None
        if self.user:
            self.cart, _ = Cart.objects.get_or_create(student=self.user.student)
            if self.event and self.cart:
                self.event_cart_item, created = EventCartItem.objects.get_or_create(
                    basecart=self.cart,
                    event=self.event
                )
        super().__init__(*args, **kwargs)
        
    class Meta:
        """Form options."""
        
        model = Cart
        fields = [
            'early_bird_to_add', 'standard_to_add', 'membership'
        ]
        widgets = {
            'student': forms.HiddenInput(),
            'event_cart_item': forms.HiddenInput(),
        }
    
    def _get_available_ticket_quantities(self, ticket_type):
        """
        Get the available ticket quantities for the specified ticket type.
        
        Parameters
        ----------
        ticket_type : str
            The given ticket type.

        Returns
        -------
        int
            The available quantity of tickets for the specified type.
        """
        
        ticket_inventory = Event.get_event_ticket_inventory(
            self.event, 
            ticket_type
        )
        total_quantity_in_cart = self.cart.get_ticket_quantity_in_cart_per_event(self.event, ticket_type)
        available_quantity = max(ticket_inventory - total_quantity_in_cart, 0)
        return available_quantity

    def save(self, commit=True):
        """Save the form data to the database.
        
        Returns
        -------
        cart
            The user's cart object.
        """
        
        # Extract values from cleaned_data dictionary
        membership = self.cleaned_data['membership']
        early_bird_to_add = 0
        standard_to_add = 0
        if 'early_bird_to_add' in self.cleaned_data and self.cleaned_data['early_bird_to_add']:
            early_bird_to_add = int(self.cleaned_data['early_bird_to_add'])
        if 'standard_to_add' in self.cleaned_data and self.cleaned_data['standard_to_add']:
            standard_to_add = int(self.cleaned_data and self.cleaned_data['standard_to_add'])
        
        # Update objects and save to database
        self.update_event_cart_item(early_bird_to_add, standard_to_add)
        self.update_cart(membership)
        self.save_objects()
        return self.cart

    def update_event_cart_item(self, early_bird_to_add, standard_to_add):
        """Set the attributes of the EventCartItem object.

        Parameters
        ----------
        early_bird_to_add : int
            The number of early bird tickets to add to cart.
        standard_to_add : int
            The number of standard tickets to add to cart.
        """
        
        if self.event_cart_item:
            self.event_cart_item.early_bird_quantity += early_bird_to_add
            self.event_cart_item.standard_quantity += standard_to_add
            self.event_cart_item.save()
        
    def update_cart(self, membership):
        """
        Set the attributes of the Cart object.
        
        Parameters
        ----------
        membership : Society
            The society membership to add or remove.
            
        Note
        ----
        This function is used in both AddToCartForm and UpdateCartForm.
        The cart is updated by updating and adding event cart item to it, which 
        is handled in the BaseCartForm.
        The cart can also be updated by adding and removing membership, which is
        handled in the AddToCartForm and UpdateCartForm respectively.
        """
        
        self.cart.event_cart_item.add(self.event_cart_item)    

    def save_objects(self):
        """Save the objects to the database"""
        
        if self.event_cart_item:
            self.event_cart_item.save()
        self.cart.save()