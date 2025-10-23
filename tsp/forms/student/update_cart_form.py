from django import forms
from tsp.forms.student.base_cart_form import BaseCartForm
from tsp.models import Society, Cart

class UpdateCartForm(BaseCartForm):
    """
    Form to update an item in the cart.
    A student can increase or decrease the number of event tickets added, and 
    remove the society membership from the cart. 
    """
    
    membership = forms.ModelChoiceField(
        queryset=Society.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        """Initialize the class instance."""
        
        membership = kwargs.pop('membership', None)
        super().__init__(*args, **kwargs)
        if membership:
            self.fields['membership'].queryset = Society.objects.filter(id=membership.id)
            self.fields['membership'].initial = membership   
    
    class Meta:
        """Form options."""
        
        model = Cart
        fields = ['membership']     
        
    def update_cart(self, membership):
        """
        Set the attributes of the Cart object when a membership is removed.
        
        Parameters
        ----------
        membership : Society
            The society membership to remove from the Cart.
        """
        
        self.cart.membership.remove(membership)
        super().update_cart(membership)