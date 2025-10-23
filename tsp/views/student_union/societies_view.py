from django.views.generic import ListView
from tsp.views.helpers import StudentUnionAccessMixin
from tsp.models import Society, University
from tsp.forms.student_union.all_societies_form import AllSocietiesForm

class SocietiesView(StudentUnionAccessMixin, ListView):
    """View that displays a list of all societies."""

    model = Society
    form_class = AllSocietiesForm
    template_name = 'student_union/societies_list.html'
    selected_option = "King's College London"

    def get_queryset(self):
        """
        Get the queryset of all societies in the same university as the student union.

        Returns
        -------
        queryset
            The queryset of societies to be displayed in the view that is
            filtered based on the value of user selection.
        """
        
        ordering = self.request.GET.get('ordering', self.selected_option)
        self.selected_option = ordering
        user = self.request.user
        return Society.objects.filter(university=user.university)