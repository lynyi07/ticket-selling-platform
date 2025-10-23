from django import forms
from django.contrib.auth import authenticate

class LogInForm(forms.Form): 
    """Form for users to login."""

    email = forms.CharField(label="Email address", widget=forms.TextInput(attrs={'placeholder':'Enter Email...'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter Password...'}))

    def get_user(self):
        """
        Check for a valid user.

        Returns:
        -------
        user 
            The current user.
        """

        user = None 
        if self.is_valid(): 
            email = self.cleaned_data.get('email').lower()
            password = self.cleaned_data.get('password') 
            user = authenticate(email=email, password=password)
        return user