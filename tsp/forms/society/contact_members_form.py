from django import forms

class ContactCommitteeMembersForm(forms.Form): 
    """Form for when society accounts want to send emails to committee members."""

    email_header = forms.CharField(
        label="Email Header", 
        widget=forms.TextInput(attrs={'placeholder':'Enter Email Header...'})
    ) 
    email_message = forms.CharField(widget=forms.Textarea())

    def get_header(self):
        """
        Check for a valid header.

        Returns:
        -------
        str
            The header of the email.
        """

        email_header = None 
        if self.is_valid(): 
            email_header = self.cleaned_data.get('email_header') 
        return email_header 

    def get_message(self):
        """
        Check for a valid message.

        Returns:
        -------
        str
            The message of the email.
        """

        email_message = None 
        if self.is_valid(): 
            email_message = self.cleaned_data.get('email_message') 
        return email_message