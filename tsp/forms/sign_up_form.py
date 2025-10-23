from django import forms
from ..models import Student, University, Domain
from django.core.validators import RegexValidator
import re

class SignUpForm(forms.ModelForm):
    """Form for users to sign up."""

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email']

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}.*$',
            message='Password must contain uppercase, lowercase and number, and must be at'
                'least 8 characters long'
            )]
    )
    password_confirmation = forms.CharField(label="Password Confirmation", widget=forms.PasswordInput())

    def clean(self):
        """Clean and validate the form data."""
        
        super().clean()
        new_password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirmation")
        email = self.cleaned_data.get("email")
        try:
            domain_name = re.findall("@[a-zA-Z0-9.]*", email)[0][1:]
            if not Domain.objects.filter(name=domain_name).exists():
                self.add_error("email", "Email is not associated with any university")
        except:
            pass
        if (new_password != password_confirm):
            self.add_error('password_confirmation', 'Password does not match')
        try:
            Student.objects.get(email = email.lower())
            self.add_error("email", "Student already exists")
        except:
            pass

    def save(self):
        """
        Save the form data to the database as a new student.

        Returns:
        -------
        user 
            The newly created student.
        """

        super().save(commit=False)
        email = self.cleaned_data.get("email").lower()
        domain = re.findall("@[a-zA-Z0-9.]*", email)[0][1:]
        university_id = Domain.objects.get(name = domain).university.id

        user = Student.objects.create_user(
            email=email,
            password = self.cleaned_data.get('password'),
            first_name = self.cleaned_data.get('first_name'),
            last_name = self.cleaned_data.get('last_name'),
            university = University.objects.get(id = university_id),
            role = 'STUDENT',
            is_superuser = False,
        )
        return user