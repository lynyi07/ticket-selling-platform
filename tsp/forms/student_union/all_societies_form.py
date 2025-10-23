from django import forms
from tsp.models import Society

class AllSocietiesForm(forms.ModelForm):
    """Form to view a Society."""

    class Meta:
        model = Society
        fields = ['name','student_union']