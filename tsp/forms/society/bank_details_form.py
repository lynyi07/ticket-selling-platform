from django.forms import ModelForm
from tsp.models import Society

class BankDetailsForm(ModelForm):
    """Form to set bank details for a society."""
    
    class Meta:
        model = Society
        fields = ['account_number', 'sort_code', 'account_name']
    
    def clean(self):
        """
        Clean the data and generate any error messages.
        
        Returns:
        -------
        dict
            The cleaned form data.
        """
    
        cleaned_data = super().clean()
        account_number = cleaned_data.get('account_number')
        sort_code = cleaned_data.get('sort_code')
        account_name = cleaned_data.get('account_name')
        if account_number and not account_number.isdigit():
            self.add_error('account_number', 'Account number must contain only digits.')
        if sort_code and not sort_code.isdigit():
            self.add_error('sort_code', 'Sort code must contain only digits.')
        if sort_code and len(sort_code) != 6:
            self.add_error('sort_code', 'Sort code must be 6 digits.')
        if account_number and len(account_number) != 8:
            self.add_error('account_number', 'Account number must be 8 digits.')
        if not account_number:
            self.add_error('account_number', 'Account number must not be empty.')
        if not sort_code:
            self.add_error('sort_code', 'Sort code must not be empty.')
        if not account_name:
            self.add_error('account_name', 'Account name must not be empty.')
        if account_name and any(char.isdigit() for char in account_name):
            self.add_error('account_name', 'Account name should not contain digits.')
        return cleaned_data