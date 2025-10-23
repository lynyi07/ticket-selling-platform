from tsp.views.helpers import StudentUnionAccessMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from tsp.models import Society

class SocietyProfileView(StudentUnionAccessMixin, DetailView):
    """View that displays a profile page for a selected society account."""   

    model = Society 
    template_name = 'student_union/society_profile_page.html'
    context_object_name = "society"
    
    def get_object(self):   
        """
        Get the requested society object and check if it belongs to the same
        university as the student union. Raise a 404 error if the condition 
        is not met.

        Returns
        -------
        Society
            The requested society object if it belongs to the same university 
            as the student union.
        Http404
            If the society does not belong to the same university as the student 
            union.
        """
        
        society_pk = self.kwargs.get('pk')
        student_union = self.request.user.studentunion
        
        return get_object_or_404(   
            Society, 
            pk=society_pk,
            university=student_union.university
        )
    