from django import forms

class ForgetPasswordForm(forms.Form): 
    """Form for users when they forget their password."""

    email = forms.EmailField(label="Email address", widget=forms.TextInput(attrs={'placeholder':'Enter Email...'}))

    def get_email(self): 
        """
        Check for a valid email.

        Returns:
        -------
        str
            The inputted email.
        """

        email = None 
        if self.is_valid(): 
            email = self.cleaned_data.get('email') 
        return email