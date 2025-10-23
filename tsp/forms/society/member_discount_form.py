from django.forms import ModelForm, NumberInput
from tsp.models import Society

class MemberDiscountForm(ModelForm):
    """Form to manage member discount for a society."""
    
    class Meta:
        model = Society
        fields = ['member_discount']
        widgets = {
            'member_discount': NumberInput(),
        }
    
    def clean(self):
        """
        Clean the data and generate any error messages.
        
        Returns:
        -------
        dict
            The cleaned form data.
        """
        
        discount = self.cleaned_data.get('member_discount')
        if discount:
            if discount < 0:
                self.add_error(
                    'member_discount', 
                    "The minimum member discount percentage is 0.00%."
                )
            if discount > 100:
                self.add_error(
                    'member_discount', 
                    "The maximum member discount percentage is 100.00%."
                )
        return self.cleaned_data