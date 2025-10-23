from django.shortcuts import redirect, get_object_or_404
from tsp.models import Society, Student
from tsp.views.helpers import StudentAccessMixin 
from django.views import View

class SubscribeSocietyView(StudentAccessMixin, View):
    """
    View for students to subscribe a society's email list to get notification 
    when this society organises new events.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to the subscribe society view.

        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.

        Returns
        -------
        HttpResponseRedirect
            A redirect response to the events list page.
        """
        
        society_pk = request.POST.get('society_pk')
        society = get_object_or_404(Society, pk=society_pk)
        student = request.user.student
        if student in society.subscribers:
            society.remove_subscriber(student)
        else:
            society.add_subscriber(student)
        return redirect('society_page', society_pk)