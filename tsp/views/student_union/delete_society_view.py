from django.shortcuts import redirect
from django.views import View  
from tsp.views.helpers import StudentUnionAccessMixin
from tsp.models import Society
from django.contrib import messages

class DeleteSocietyView(StudentUnionAccessMixin, View): 
    """View that allows a student union to delete a society."""
    
    http_method_names = ['post']

    def post(self, request):
        """
        Handle the POST request to the delete society view.
        
        Parameters
        ----------
        request : HttpRequest
            The request object for the HTTP request.
        society_id : int
            The society's id

        Returns
        -------
        HttpResponseRedirect
            A redirected response to the view societies page.
        """

        try: 
            society = Society.objects.get(id=request.POST['society_id'])
            messages.add_message(
                request, 
                messages.SUCCESS, 
                f"Society: {society.name} successfully removed!"
            )
            society.delete()
            return redirect("view_societies")
        except Society.DoesNotExist:
            messages.add_message(
                request, 
                messages.ERROR, 
                "Society does not exist!"
            )
            return redirect("view_societies")