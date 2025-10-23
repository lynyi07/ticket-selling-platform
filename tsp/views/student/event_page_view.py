from django.views.generic import DetailView
from django.http import Http404
from tsp.models import Event 
from tsp.forms.student.add_to_cart_form import AddToCartForm
from tsp.views.helpers import StudentAccessMixin 

class StudentEventPageView(StudentAccessMixin, DetailView):
    """
    View that displays events that can be saved by the student
    alongside its details. The student can add event ticket to
    the cart.
    """

    model = Event
    template_name = 'student/event_page.html'
    context_object_name = 'event'
    form_class = AddToCartForm
    
    @property
    def student(self):
        """
        Get the student associated with the current user.

        Returns
        -------
        Student
            The current user's student object.
        """
        
        return self.request.user.student
    
    def get_object(self):
        """
        Get the requested event object and check if it belongs to the same
        university as the student. Raise a 404 error if the condition is not met.

        Returns
        -------
        event : Event
            The event object for the current request.

        Raises
        ------
        Http404
            If the event does not belong to the same university as the student.
        """
            
        events = Event.objects.filter(society__university=self.student.university)
        event = super().get_object()
        if event not in events:
            raise Http404()
        return event

    def get(self, request, *args, **kwargs):
        """
        Handle the GET request to the student event page view.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.

        Returns
        -------
        HttpResponse
            Render the event page with the add to cart form.
        Http404
            If the event is not found in the filtered events from the 
            get_object() method, which retrieves events belonging to the same 
            university as the student.
        """
    
        self.object = self.get_object()
        form = self.form_class(user=request.user, event=self.object)
        context = self.get_context_data(object=self.object, form=form)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        """
        Get the context data to be used in rendering the template.

        Returns
        -------
        dict
            A dictionary containing the following key(s):
            - 'student': The current student's id
        """
        
        context = super().get_context_data(**kwargs)
        context['student'] = self.student
        return context

