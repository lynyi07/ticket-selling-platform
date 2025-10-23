from django import forms
from django.core.validators import RegexValidator

class ChangePasswordForm(forms.Form):
    """Form enabling users to change their password."""
    
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        #Set the standard of security the password must be
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}.*$', 
            message='Password must contain uppercase, lowercase and number, '
                    'and must be at least 8 characters long'
            ) 
        ]
    )
    password_confirmation = forms.CharField(
        label='Password confirmation', 
        widget=forms.PasswordInput()
    )

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error(
                'password_confirmation', 
                'Confirmation does not match password.'
            )