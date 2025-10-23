from django import forms
from tsp.models import Society
from tsp.forms.student.base_cart_form import BaseCartForm

class AddToCartForm(BaseCartForm):
    """
    Form to add an item to the cart.
    A student can add the event ticket or society membership to the cart.
    """
    
    membership = forms.ModelChoiceField(
        queryset=Society.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    standard_to_add = forms.ChoiceField(
        choices=[('', '-----')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    early_bird_to_add = forms.ChoiceField(
        choices=[('', '-----')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    def __init__(self, *args, **kwargs):
        """Initialize the class instance."""
        
        super().__init__(*args, **kwargs)
        self._set_membership_choices()
        self._set_ticket_options()
        
    def _set_membership_choices(self):
        """
        Set the available membership choices for the form based on the event 
        and user's university. Filter societies that accept new members.
        """
        
        if self.user and self.event:
            university = self.user.university
            all_societies = self.event.society.filter(university=university)
            society_ids = [
                society.pk
                for society in all_societies 
                if society.accept_new_member
            ]
            self.membership_choices = all_societies.filter(id__in=society_ids)
            self.fields['membership'].queryset = self.membership_choices
            self.fields['membership'].label = (
                "Unlock member benefits - "
                "become a member today!"
            )
            self.fields['membership'].choices = [('', '-----')] + list(
                map(self._get_membership_label, self.membership_choices)
            )
            
    def _get_membership_label(self, membership):
        """
        Get a tuple with the value and label to use for a membership option in 
        the form's drop-down list.

        Parameters
        ----------
        membership : Society
            The society object for the membership.

        Returns
        -------
        tuple
            A tuple containing the value and label for the membership option in 
            the form's drop-down list.
        """
    
        value = str(membership.pk)
        label = f"{membership.name} £{membership.member_fee}"
        return (value, label)
    
    def _set_ticket_options(self):
        """
        Set the choices and widget attributes for the early bird and standard 
        ticket quantity fields based on the event's available ticket inventory 
        and the quantities of these tickets that have already been added to the 
        user's cart.

        Standard ticket is not released until early bird tickets are sold out or 
        have been added to the user's cart.
        
        If both early bird and standard tickets are sold out or have been added 
        to the cart, disable both quantity fields and set their labels to 
        indicate that they are sold out.
        """

        early_bird_availability = self._get_available_ticket_quantities('early_bird')
        standard_availability = self._get_available_ticket_quantities('standard')
        
        early_bird_choices = self._get_ticket_choices(early_bird_availability)
        standard_choices = self._get_ticket_choices(standard_availability)

        if early_bird_availability > 0:
            self._set_ticket_options_helper(
                False, 'Early Bird Ticket', early_bird_choices,
                True, 'Standard Ticket (Not Released)',  [('', '-----')]
            )
        elif standard_availability > 0:            
            self._set_ticket_options_helper(
                True, 'Early Bird Ticket (Sold Out)', [('', '-----')],
                False, 'Standard Ticket',  standard_choices
            )
        else:                
            self._set_ticket_options_helper(
                True, 'Early Bird Ticket (Sold Out)', [('', '-----')],
                True, 'Standard Ticket (Sold Out)',  [('', '-----')]
            )
    
    def _get_ticket_choices(self, ticket_availability):
        """
        Get a list of ticket choices with the corresponding integer values.
        
        Parameters
        ----------
        ticket_availability : int
            The number of available tickets for the specified ticket type.

        Returns
        -------
        List[Tuple[int, str]]
            A list of ticket choices with the corresponding integer values.
        """
        
        ticket_choices = [
            (i, str(i)) 
            for i in range(1, ticket_availability + 1)
        ]
        return ticket_choices
    
    def _set_ticket_options_helper(
        self, early_bird_disabled, early_bird_label, early_bird_choices, 
        standard_disabled, standard_label, standard_choices
    ):
        """
        Set the ticket options for the form fields.
        
        Parameters
        ----------
        early_bird_disabled : bool
            A boolean value indicating whether the early bird ticket field is 
            disabled.
        early_bird_label : str
            A string specifying the label of the early bird ticket field.
        early_bird_choices : list of tuple
            Choices for the early bird ticket quantity field.
        standard_disabled : bool
            A boolean value indicating whether the standard ticket field is 
            disabled.
        standard_label : str
            A string specifying the label of the standard ticket field.
        standard_choices : list of tuple
            Choices for the standard ticket quantity field.
        """
        
        self.fields['early_bird_to_add'].widget.attrs['disabled'] = early_bird_disabled
        self.fields['early_bird_to_add'].label = early_bird_label
        self.fields['early_bird_to_add'].choices = early_bird_choices
        self.fields['standard_to_add'].widget.attrs['disabled'] = standard_disabled
        self.fields['standard_to_add'].label = standard_label
        self.fields['standard_to_add'].choices = standard_choices
        
    def clean(self):
        """
        Validate the form's cleaned_data.

        Check if the user is already a member of the society selected or if the
        membership is already added to the cart.

        Returns:
        -------
        dict
            The cleaned form data.
        """
    
        cleaned_data = super().clean()
        membership = cleaned_data.get('membership')
        
        # Check if the student is already a member
        if self.cart.user_is_member(membership):
            self.add_error('membership', 'You are already a member.')
        
        # Check if the student has already added the same membership
        if self.cart.membership_is_in_cart(membership):
            self.add_error('membership', 'You can only add it once.')
            
        return cleaned_data
        
    def update_cart(self, membership):
        """
        Set the attributes of the Cart object when a membership is added.
        
        Parameters
        ----------
        membership : Society
            The society membership to add to the Cart.
        """
        
        self.cart.membership.add(membership)
        super().update_cart(membership)