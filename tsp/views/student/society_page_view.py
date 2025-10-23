from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from tsp.models import Society
from tsp.views.helpers import StudentAccessMixin 

class SocietyPageView(StudentAccessMixin, DetailView):
    """
    View that displays a society's details and allows users to follow and 
    subscribe to the society's emailing list.
    """

    model = Society
    template_name = 'student/society_page.html'
    context_object_name = 'society'

    def get_object(self):   
        """
        Get the requested society object and check if it belongs to the same
        university as the student. Raise a 404 error if the condition is not 
        met.

        Returns
        -------
        Society
            The requested society object if it belongs to the same university 
            as the student.
        Http404
            If the society does not belong to the same university as the student.
        """
        
        society_pk = self.kwargs.get('pk')
        student = self.request.user.student
        
        return get_object_or_404(   
            Society, 
            pk=society_pk,
            university=student.university
        )

    def get_context_data(self, **kwargs):
        """
        Get the context data to be used in rendering the template.
        
        Returns
        -------
        dict
            A dictionary containing the following key(s):
            - 'is_member': Whether the current user is a regular member or 
                           committee member of the society.
            - 'is_follower': Whether the current user is following the society.
            - 'is_subscribed': Whether the current user is subscribed to the 
                               society's emailing list.
        """

        context = super().get_context_data(**kwargs)
        student = self.request.user.student
        society = self.get_object()
        context['is_member'] = society.is_student_member(student)
        context['is_follower'] = student in society.followers
        context['is_subscriber'] = student in society.subscribers
        return context
