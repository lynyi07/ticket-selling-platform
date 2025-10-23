from django import forms
from tsp.models import University, Domain, Society, StudentUnion
import re

class CreateSocietyForm(forms.ModelForm):
    """Form to allow student unions to create a Society."""

    class Meta:
        model = Society
        fields = ['name', 'email']

    def clean(self):
        """Clean and validate the form data."""

        super().clean()
        email = self.cleaned_data.get("email")
        name = self.cleaned_data.get('name')
        try:
            domain_name = re.findall("@[a-zA-Z0-9.]*", email)[0][1:]
            if not Domain.objects.filter(name=domain_name).exists():
                self.add_error("email", "Email is not associated with any university")

            university_id = Domain.objects.get(name = domain_name).university.id
            university_abbreviation = University.objects.get(pk=university_id).abbreviation
            if Society.objects.filter(name=university_abbreviation + " " + name).exists():
                self.add_error('name', 'A society with this name already exists')
        except:
            pass
        
    def save(self):
        """
        Save the form data to the database as a new society.

        Returns:
        -------
        society 
            The newly created society.
        """

        super().save(commit=False)
        email = self.cleaned_data.get("email")
        domain = re.findall("@[a-zA-Z0-9.]*", email)[0][1:]
        university_id = Domain.objects.get(name = domain).university.id
        university_abbreviation = University.objects.get(pk=university_id).abbreviation
        university_email = f'{university_abbreviation.lower()}su@{domain}'

        society = Society.objects.create_user(
            email=self.cleaned_data.get("email"),
            password = "Password123",
            student_union = StudentUnion.objects.get(email = university_email),
            name = university_abbreviation + " " + self.cleaned_data.get('name'),
            university = University.objects.get(id = university_id),
            role = 'SOCIETY',
            is_superuser = False,
        )
        return society