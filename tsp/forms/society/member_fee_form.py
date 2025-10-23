from django.forms import ModelForm, NumberInput
from tsp.models import Society

class MemberFeeForm(ModelForm):
    """Form to set annual member fee for a society."""
    
    class Meta:
        model = Society
        fields = ['member_fee']
        widgets = {
            'member_fee': NumberInput(),
        }

    def clean(self):
        """
        Clean the data and generate any error messages.
        
        Returns:
        -------
        dict
            The cleaned form data.
        """
        
        fee = self.cleaned_data.get('member_fee')
        if fee and fee < 0:
            self.add_error(
                'member_fee', 
                "The minimum member fee is 0.00"
            )
        return self.cleaned_data