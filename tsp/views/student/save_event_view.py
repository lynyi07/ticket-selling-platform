from django.shortcuts import get_object_or_404
from django.views.generic.edit import View
from django.shortcuts import redirect 
from tsp.models import Event 
from tsp.views.helpers import StudentAccessMixin

class SaveEventView(StudentAccessMixin, View):
    """
    View that allows students to save an event so that this event can be 
    displayed on For You page.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to the save event view.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.
       
        Returns
        -------
        HttpResponseRedirect
            A redirect response to the event page.
        """
        
        event_pk = request.POST['event_pk']
        event = get_object_or_404(Event, pk=event_pk)
        student = request.user.student
        if student.event_saved(event):
            student.unsave_event(event)
        else:
            student.save_event(event)
        return redirect('event_page', pk=event_pk)