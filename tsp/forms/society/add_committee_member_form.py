from django import forms
from tsp.models import Student, Society

class AddCommitteeMemberForm(forms.Form):
    """Form to add committee members to a society."""

    email = forms.CharField(
        label="Email address",
        widget=forms.TextInput(attrs={'placeholder':'Enter Email...'})
    )
    
    def __init__(self, *args, **kwargs):
        """Initialize the form with the society instance."""
        
        self.society = kwargs.pop('society', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        """
        Validate if the email belongs to an existing student, if the student 
        is already a committee member, or if they belong to the same university 
        as the society.
        
        Returns:
        -------
        dict
            The cleaned form data.
        """

        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        try:
            student = Student.objects.get(email=email)
            if self.society:
                if student in self.society.committee_members:
                    self.add_error(
                        'email', 
                        'The student is already a committee member of this '
                        'society.'
                    )
                elif student.university != self.society.university:
                    self.add_error(
                        'email', 
                        'This student does not belong to the same university '
                        'as the society.'
                    )
                cleaned_data['student'] = student
        except Student.DoesNotExist:
            self.add_error(
                'email', 
                'This email does not belong to any student.'
            )
        return cleaned_data
